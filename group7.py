# List your names:
 #Swayon Bhunia
 #Mayank Pratap Singh Chauhan
 #Ajesh Sukumaran Nair
def decode(payload):
    """
    Decode the payload buffer into a temperature value.

    This function returns the temperature value.
    """

    # Update this function to return the temperature value.
    if len(payload) < 2:
        return None
    temp_data = (payload[0] << 8) | payload[1]
    temperature = temp_data / 100.0
    return temperature
