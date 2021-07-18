import settings  # Load enviroment variables

from sensor_node.sensor_node import SensorNode, SensorNodeCreationError

# Script to start the sensor node
if __name__ == "__main__":

    node = None

    try:
        node = SensorNode()

        node.startup()

        node.sensing_mode()
    except SensorNodeCreationError as error:
        print("Error creating sensor node instance: ", error)
    except Exception as error:
        print("Exception: {0}".format(error))
    finally:
        if node is not None:
            node.communication_module.close_connections()
        else:
            print("Failed to create a sensor node instance!")
