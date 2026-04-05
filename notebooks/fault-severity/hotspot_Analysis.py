#py "C:\Users\Extra\Desktop\2nd-Year-DGSP-Github\Model\Hotspot\hotspot_Analysis.py"
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# -------------------------------
#The image path

image_path = r"C:\Users\Extra\Desktop\2nd-Year-DGSP-Github\Model\Hotspot\RawImages\img1.jpg"

# Check if the image exists
if not os.path.exists(image_path):
    print("Error: Image not found. Check the path!")
    exit()

# -------------------------------
# Load the image
image = cv2.imread(image_path)
if image is None:
    print("Error: Failed to load image!")
    exit()

# -------------------------------
# Convert to grayscale
# 
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# -------------------------------
# Display heatmap
plt.imshow(gray, cmap='hot')
plt.colorbar()
plt.title("Thermal Image Heatmap")
plt.show()

# -------------------------------
#Compute hotspot metrics
Tmax = np.max(gray)
Tavg = np.mean(gray)
deltaT = Tmax - Tavg

print(f"Max pixel value (Tmax): {Tmax}")
print(f"Average pixel value (Tavg): {Tavg}")
print(f"Temperature difference (ΔT): {deltaT}")

# -------------------------------
# Asign severity
if deltaT < 5:
    severity = "Normal"
elif deltaT < 10:
    severity = "Moderate"
elif deltaT < 20:
    severity = "Severe"
else:
    severity = "Critical"

print(f"Hotspot severity: {severity}")
