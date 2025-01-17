import subprocess

# Define paths to your scripts
script1_path = 'MapPathfinder.py'
script2_path = 'YoloInference.py'

# Run script1 in a separate process
process1 = subprocess.Popen(['python', script1_path])

# Run script2 in a separate process
process2 = subprocess.Popen(['python', script2_path])

# Optionally, wait for scripts to finish
process1.wait()
process2.wait()

print("Both scripts have finished executing.")