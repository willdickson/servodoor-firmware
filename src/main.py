from door_controller import DoorController

ctlr = DoorController()
while True:
    try:
        ctlr.run()
    except Exception as err:
        continue

