# Normal Import
import GML

# Classes
from GML_Cmd.CommandServer import CommandServer as GML_CommandServer
from GML_Cmd.CommandTask import CommandTask as GML_CommandTask

# Instance
command_tasks = []
command_server = None
registered_commands = {}

# Constants
RESULT_SIGN_GOOD = "GOOD "
RESULT_SIGN_FAIL = "FAIL "


def init():
    GML.Cmd.register_command("help", "Display all commands")
    GML.Cmd.command_server = GML_CommandServer()
    GML.Cmd.command_server.launch()
    print("Cmd::Server OK.")


def register_command(command_keyword, help_text):
    registered_commands[command_keyword] = help_text


def execute_command(command_line,
                    client_socket,
                    client_address):
    command_id = len(GML.Cmd.command_tasks)
    command_task = GML_CommandTask(
        command_id=command_id,
        command_line=command_line,
        receive_datetime=GML.Sys.GML_Datetime.now(),
        client_socket=client_socket,
        client_address=client_address,
    )
    GML.Cmd.command_tasks.append(command_task)

    # Check if command is registered
    is_registered = False
    for registered_command in GML.Cmd.registered_commands.keys():
        if command_line.lower().startswith(registered_command.lower()):
            is_registered = True
            break

    if is_registered:
        if command_line == "help":
            help_str = "\n"
            for command in GML.Cmd.registered_commands.keys():
                help_str += ("%s - %s\n" % (command, GML.Cmd.registered_commands[command]))
            GML.Cmd.finish_command(command_id=command_id,
                                   result_sign=RESULT_SIGN_GOOD,
                                   result_detail=help_str)
        try:
            GML.Qt.Service.Signals.has_new_command.emit(command_id, command_line)
        except Exception as e:
            print("Cmd::execute_command::Fail to emit Signal.has_new_command: " + str(e))
    else:
        GML.Cmd.finish_command(command_id=command_id,
                               result_sign=RESULT_SIGN_FAIL,
                               result_detail="Unknown Command `%s`" % (str(command_line),))


def finish_command(command_id, result_sign, result_detail):
    command_task = GML.Cmd.command_tasks[command_id]
    result_detail = str(result_detail)
    if command_task.result or command_task.send_datetime:
        print("Cmd::finish_command::Command %i is already finished. New result does not apply: %s" % (command_id,
                                                                                                      result_detail))
    else:
        command_task.result = result_detail
        command_task.send_datetime = GML.Sys.GML_Datetime.now()
        try:
            command_task.client_socket.sendto(bytes(result_sign + result_detail, "utf-8"),
                                              command_task.client_address)
            command_task.client_socket = None
        except Exception as e:
            print("Cmd::finish_command::[Command %i: %s] Fail to send back: %s" % (command_id, result_detail, str(e)))
