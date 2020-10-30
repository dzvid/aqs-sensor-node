import settings  # Load enviroment variables

from sensor_node.sensor_node import SensorNode, SensorNodeCreationError

# Script to start the sensor node
if __name__ == "__main__":

    try:
        node = SensorNode()

        node.startup()

        node.sensing_mode()
    except SensorNodeCreationError as error:
        print("Error creating sensor node instance: ", error)
    except Exception as error:
        print("Exception: {0}".format(error))
    finally:
        SensorNode.communication_module.close_connections()
