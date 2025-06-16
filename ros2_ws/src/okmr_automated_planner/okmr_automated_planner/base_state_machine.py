import threading
from transitions import Machine
from okmr_automated_planner.state_node import StateNode
from okmr_automated_planner.movement_command_action_client import MovementCommandActionClient

class BaseStateMachine(Machine):
    mandatory_states = ['uninitialized','initializing','initialized', 'done', 'aborted']
    mandatory_transitions = [
                                { 'trigger': 'initialize', 'source': 'uninitialized', 'dest': 'initializing' },
                                { 'trigger': 'initializingDone', 'source': 'initializing', 'dest': 'initialized' },
                                { 'trigger': 'finish', 'source': '*', 'dest': 'done' },
                                { 'trigger': 'abort', 'source': '*', 'dest': 'aborted' },
                              ]
    def __init__(self, 
                 name, 
                 ros_node, 
                 states, 
                 transitions, 
                 success_callback=None, 
                 fail_callback=None, 
                 *args, **kwargs):
        self.state_cls = StateNode
        self.machine_name = name
        self.ros_node = ros_node
        self.states = states
        self.transitions = transitions
        
        self.success_callback = success_callback
        self.fail_callback = fail_callback
        
        self._subscriptions = []
        self._publishers = []
        self._timers = []
        self._clients = []
        
        # Initialize movement action client for all state machines
        self.movement_client = MovementCommandActionClient(self.ros_node)

        self.initial_start_time = None
        self.state_start_time = None

        self.record_initial_start_time() 
        # to actually be useful, initial start should be overwritten, since this is called during master state machine creation, not when the machine actually starts getting used
        #ex. call the above method inside on_enter_initialized if you want to track time since initialization

        self.record_state_start_time()

        self.success = False
        
        self.queued_method = None 
        # can be used to more cleanly immediately progress from one state to another
        #self.queued_method is called after every state change
        
        self.add_mandatory_states()
        self.add_mandatory_transitions()

        super().__init__(
            model=self, 
            states=self.states, 
            transitions=self.transitions,
            initial='uninitialized',
            after_state_change='post_state_change',
            before_state_change='pre_state_change',
            #*args,
            #**kwargs #allows for additional arguments
        )

        self.current_sub_machine = None

        period = self.ros_node.get_state_timeout_check_period()
        
        self.add_timer(f"state_timeout_check", period, self.state_timeout_check_callback)

    def get_current_state_node(self):
        #this could cause errors if you dont specifically declare every parameter as a StateNode type
        return self.get_state(self.state)

    def state_timeout_check_callback(self):
        time_since_state_start = self.get_time_since_state_start()

        self.ros_node.get_logger().debug(f"Time Since State Start {time_since_state_start}" + 
                                            f"\t Machine: {self.machine_name} \t State: {self.state}")

        timeout = self.get_current_state_node().timeout 

        if time_since_state_start >= timeout and timeout > 0:
            self.ros_node.get_logger().warn(f"State Timed Out after {time_since_state_start}" + 
                                            f"\t Machine: {self.machine_name} \t State: {self.state}")
            self.abort()

    def add_mandatory_transitions(self):
        state_names = [state.name for state in self.states]
        for state in self.mandatory_states:
            if state not in state_names:
                self.states.append(StateNode(state))

    def add_mandatory_states(self):
        mandatory_triggers = [transition['trigger'] for transition in self.mandatory_transitions]
        all_triggers = [transition['trigger'] for transition in self.transitions]
        for transition in self.mandatory_transitions:
            if transition["trigger"] not in all_triggers:
                self.transitions.append(transition)
    
    def record_initial_start_time(self):
        self.initial_start_time =  self.ros_node.get_clock().now()

    def record_state_start_time(self):
        self.state_start_time =  self.ros_node.get_clock().now()

    def get_time_since_initial_start(self):
        return (self.ros_node.get_clock().now() - self.initial_start_time).nanoseconds / float(10 ** 9)
    
    def get_time_since_state_start(self):
        return (self.ros_node.get_clock().now() - self.state_start_time).nanoseconds / float(10 ** 9)
    
    def on_completion(self):
        #to be implemented by sub classes if desired
        pass

    def pre_state_change(self):
        self.log_pre_state_change()

    def post_state_change(self):
        self.record_state_start_time()
        self.ros_node.get_logger().info(f"{self.get_current_state_node().timeout}") 
        self.log_post_state_change()
        self.check_completion()
        if self.queued_method:
            self.warn_auto_queued_method()
            method = self.queued_method
            self.queued_method = None
            method()

    def log_pre_state_change(self):
        self.ros_node.get_logger().info(f"Pre State Change  \t Machine: {self.machine_name} \t From: {self.state}")

    def log_post_state_change(self):
        self.ros_node.get_logger().info(f"Post State Change \t Machine: {self.machine_name} \t To: {self.state}")

    def warn_auto_queued_method(self):
        queued_func_name = None
        try:
            queued_func_name = self.queued_method.func.__self__.name
        except:
            try:
                queued_func_name = self.queued_method.__name__
            except:
                pass
        self.ros_node.get_logger().warn(f"Auto Queued Method\t Machine: {self.machine_name} \t From: {self.state} \t To: {queued_func_name} \t (NOT recommended outside of testing)")

    def check_completion(self):
        if self.state == 'done' or self.state == 'aborted':
            self.on_completion()
            self.cleanup_ros2_resources()
            if self.current_sub_machine and not self.current_sub_machine.is_aborted():
                self.current_sub_machine.abort()
                self.current_sub_machine = None
            #optional success and failure callbacks
            #can be used to hand control back to a parent machine
            if self.success and self.success_callback:
                self.success_callback()
            elif not self.success and self.fail_callback:
                self.fail_callback()
    
    def start_current_state_sub_machine(self, success_callback=None, fail_callback=None):
        '''
        Convenience function for starting sub state machines
        calls "initialize" trigger
        '''
        sub_machine = self.get_state(self.state).sub_machine
        self._start_sub_machine(sub_machine, success_callback, fail_callback)
    
    def _start_sub_machine(self, sub_machine, success_callback=None, fail_callback=None):
        self.current_sub_machine = sub_machine
        sub_machine.success_callback = success_callback
        sub_machine.fail_callback = fail_callback
        threading.Thread(target=sub_machine.initialize, daemon=True).start()

    '''

    ROS2 CODE

    '''

    def add_subscription(self,msg_type, topic, callback):
        sub = self.ros_node.create_subscription(msg_type, topic, callback, 10)
        self._subscriptions.append(sub)
        return sub

    def remove_subscription(self, topic):
        matching_subs = [sub for sub in self._subscriptions if sub.topic_name == topic or sub.topic_name == "/" + topic]
        for sub in matching_subs:
            try:
                self._subscriptions.remove(sub)
                self.ros_node.destroy_subscription(sub)
            except:
                pass 

    def add_publisher(self, msg_type, topic):
        pub = self.ros_node.create_publisher(msg_type, topic, 10)
        self._publishers.append(pub)
        return pub

    def publish_on_topic(self, msg_type, topic_name, msg):
        matching_pubs = [pub for pub in self._publishers if pub.topic_name == topic_name or pub.topic_name == "/" + topic_name]
        pub = None
        if len(matching_pubs) > 0:
            pub = self.matching_pubs[0]
        else:
            pub = self.add_publisher(msg_type, topic_name)
        pub.publish(msg)

    def add_timer(self, name: str, duration, callback):
        timer = self.ros_node.create_timer(duration, callback)
        self._timers.append({"f{self.machine_name}_{name}": timer})
        return timer

    def remove_timer(self, name):
        self.ros_node.destroy_timer(self._timers[name])
        self._timers.pop(name)

    def add_service_client(self, service_type, service_name):
        cli = self.create_client(service_type, service_name)
        #unchecked, service may not exist
        self._clients.append({service_name: cli})
        return cli

    def send_service_request(self, service_type, service_name, srv_msg, done_callback):
        cli = None
        if service_name in self._clients:
            cli = self._clients[service_name]
        else:
            cli = self.add_service_client(service_type, service_name)
        cli.call_async(srv_msg).add_done_callback(done_callback)

    def cleanup_ros2_subscriptions(self):
        for sub in self._subscriptions:
            try:
                self.ros_node.destroy_subscription(sub)
            except:
                pass
        self._subscriptions.clear()

    def cleanup_ros2_publishers(self):
        for sub in self._publishers:
            try:
                self.ros_node.destroy_publisher(pub)
            except:
                pass
        self._publishers.clear()

    def cleanup_ros2_timers(self):
        for name in self._timers:
            try:
                self.ros_node.destroy_timer(self._timers[name])
            except:
                pass
        self._timers.clear()

    def cleanup_ros2_clients(self):
        self._clients.clear()

    def cleanup_movement_client(self):
        """Clean up the movement action client"""
        self.movement_client.cleanup()

    def cleanup_ros2_resources(self):
        '''
        Cleans up all ROS2 resources from ONLY THIS MACHINE
        '''
        self.cleanup_ros2_subscriptions()
        self.cleanup_ros2_publishers()
        self.cleanup_ros2_timers()
        self.cleanup_ros2_clients()
        self.cleanup_movement_client()
