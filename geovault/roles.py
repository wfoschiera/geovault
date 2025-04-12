from rolepermissions.roles import AbstractUserRole

CAN_SEE_USER_DATA = "can_see_user_data"
CAN_ADD_FARMER_USERS = "can_add_farmer_users"
CAN_SEND_FILES = "can_send_files"
CAN_REMOVE_FILES = "can_remove_files"
CAN_PROCESS_FILES = "can_process_files"


class FarmerUser(AbstractUserRole):
    role_name = "FarmerUser"

    available_permissions = {
        CAN_SEND_FILES: True,
        CAN_REMOVE_FILES: True,
    }


class FarmerAdmin(AbstractUserRole):
    role_name = "FarmerUser"

    available_permissions = {
        CAN_SEND_FILES: True,
        CAN_REMOVE_FILES: True,
        CAN_ADD_FARMER_USERS: True,
    }
