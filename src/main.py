import settings  # Load enviroment variables

from sensor_node.sensor_node import SensorNode, SensorNodeCreationError

# Script to start the sensor node
if __name__ == '__main__':

    try:
        node = SensorNode()

        node.begin()

        node.sensing_mode()
    except SensorNodeCreationError as error:
        print("Error creating the sensor node instance: ", error)
    except Exception as error:
        print("Exception: {0}".format(error))
