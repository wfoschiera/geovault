from rolepermissions.roles import AbstractUserRole

CAN_SEE_USER_DATA = "can_see_user_data"
CAN_ADD_FARMER_USERS = "can_add_farmer_users"
CAN_SEND_FILES = "can_send_files"
CAN_MOVE_FILES = "can_remove_files"
CAN_PROCESS_FILES = "can_process_files"
CAN_DELETE_FILES = "can_delete_files"


class Farmer(AbstractUserRole):
    role_name = "Farmer"

    available_permissions = {
        CAN_SEND_FILES: True,
        CAN_MOVE_FILES: True,
    }


class FarmerAdmin(AbstractUserRole):
    role_name = "FarmerAdmin"

    available_permissions = {
        CAN_SEND_FILES: True,
        CAN_MOVE_FILES: True,
        CAN_ADD_FARMER_USERS: True,
    }


class Technician(AbstractUserRole):
    role_name = "Technician"

    available_permissions = {
        CAN_SEND_FILES: True,
        CAN_MOVE_FILES: True,
        CAN_DELETE_FILES: True,
    }
