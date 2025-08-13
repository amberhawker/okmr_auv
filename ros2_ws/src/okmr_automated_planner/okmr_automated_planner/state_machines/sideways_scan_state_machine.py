from okmr_automated_planner.base_state_machine import BaseStateMachine
from okmr_utils.logging import make_green_log
from okmr_msgs.msg import MissionCommand, MovementCommand


class SidewaysScanStateMachine(BaseStateMachine):
    
    PARAMETERS = [
        {'name': 'moving_sideways_distance',
         'value': 1,
         'descriptor': 'distance to move sideways in meters'},
    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moving_sideways_distance = self.get_local_parameter("moving_sideways_distance")
        
    def on_enter_initializing(self):
        self.queued_method = self.initialized
        
    def on_enter_moving_sideways(self):
        movement_msg = MovementCommand()
        movement_msg.command = MovementCommand.MOVE_RELATIVE
        movement_msg.translation.x = self.moving_sideways_distance
        
        success = self.movement_client.send_movement_command(
            movement_msg,
            on_success=self.moving_sideways_done,
            on_failure=self.abort,
        )
        
        if not success:
            self.ros_node.get_logger().error("Failed to send sideways movement command")
            self.queued_method = self.abort
    
    # need to figure out how to save initial position first
    # def on_enter_returning_to_center(self):
    #     movement_msg = MovementCommand()
    #     movement_msg.command = MovementCommand.MOVE_RELATIVE
    #    # movement_msg.translation.x = 
        
    #     success = self.movement_client.send_movement_command(
    #         movement_msg,
    #         on_success=self.returning_to_center_done,
    #         on_failure=self.abort,
    #     )
        
    #     if not success:
    #         self.ros_node.get_logger().error("Failed to send return to center command")
    #         self.queued_method = self.abort
            