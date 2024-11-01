import math
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd

# INPUTS: Date and location
# OUTPUTS: Azimuth and elevation of sun
def sunPosition(year, month, day, hour=12, m=0, s=0, lat=43.5, long=-80.5):
    twopi = 2 * math.pi
    deg2rad = math.pi / 180

    # Get day of the year, e.g. Feb 1 = 32, Mar 1 = 61 on leap years
    len_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30]
    day = day + np.cumsum(len_month)[month-1]
    leapdays = (year % 4 == 0 and (year % 400 == 0 or year % 100 != 0) and day >= 60 and not (month == 2 and day == 60))
    day += int(leapdays)

    # Get Julian date - 2400000
    hour = hour + m / 60 + s / 3600  # hour plus fraction
    delta = year - 1949
    leap = math.floor(delta / 4)  # former leap years
    jd = 32916.5 + delta * 365 + leap + day + hour / 24

    # The input to the Astronomer's almanach is the difference between
    # the Julian date and JD 2451545.0 (noon, 1 January 2000)
    time = jd - 51545.

    # Ecliptic coordinates
    # Mean longitude
    mnlong = 280.460 + 0.9856474 * time
    mnlong = mnlong % 360
    mnlong += int(mnlong < 0) * 360

    # Mean anomaly
    mnanom = 357.528 + 0.9856003 * time
    mnanom = mnanom % 360
    mnanom += int(mnanom < 0) * 360
    mnanom = mnanom * deg2rad

    # Ecliptic longitude and obliquity of ecliptic
    eclong = mnlong + 1.915 * math.sin(mnanom) + 0.020 * math.sin(2 * mnanom)
    eclong = eclong % 360
    eclong += int(eclong < 0) * 360
    oblqec = 23.439 - 0.0000004 * time
    eclong = eclong * deg2rad
    oblqec = oblqec * deg2rad

    # Celestial coordinates
    # Right ascension and declination
    num = math.cos(oblqec) * math.sin(eclong)
    den = math.cos(eclong)
    ra = math.atan(num / den)
    ra += int(den < 0) * math.pi
    ra += int(den >= 0 and num < 0) * twopi
    dec = math.asin(math.sin(oblqec) * math.sin(eclong))

    # Local coordinates
    # Greenwich mean sidereal time
    gmst = 6.697375 + 0.0657098242 * time + hour
    gmst = gmst % 24
    gmst += int(gmst < 0) * 24

    # Local mean sidereal time
    lmst = (gmst + long / 15.)
    lmst = lmst % 24.
    lmst += int(lmst < 0) * 24.
    lmst = lmst * 15. * deg2rad

    # Hour angle
    ha = lmst - ra
    ha += int(ha < -math.pi) * twopi
    ha -= int(ha > math.pi) * twopi

    # Latitude to radians
    lat = lat * deg2rad

    # Azimuth and elevation
    el = math.asin(math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(ha))
    az = math.asin(-math.cos(dec) * math.sin(ha) / math.cos(el))

    # For logic and names, see Spencer, J.W. 1989. Solar Energy. 42(4):353
    cosAzPos = (0 <= math.sin(dec) - math.sin(el) * math.sin(lat))
    sinAzNeg = (math.sin(az) < 0)
    az += int(cosAzPos and sinAzNeg) * twopi
    if not cosAzPos:
        az = math.pi - az

    el = el / deg2rad
    az = az / deg2rad
    lat = lat / deg2rad

    return az, el

# Function to generate and plot sun position over a day, including zenith angle
def plot_sun_path(year, month, day, lat=43.5, long=-80.5):
    hours = np.arange(0, 24, 0.25)  # Generate times throughout the day in 15-minute intervals
    azimuths = []
    elevations = []
    zeniths = []

    for hour in hours:
        az, el = sunPosition(year, month, day, hour=hour, m=0, s=0, lat=lat, long=long)
        azimuths.append(az)
        elevations.append(el)
        zeniths.append(90 - el)  # Zenith angle calculation

    # Find max and min values
    max_az = max(azimuths)
    min_az = min(azimuths)
    max_el = max(elevations)
    min_el = min(elevations)
    max_zenith = max(zeniths)
    min_zenith = min(zeniths)

    # Print max and min values
    print(f"Max Azimuth: {max_az:.2f}°, Min Azimuth: {min_az:.2f}°")
    print(f"Max Elevation: {max_el:.2f}°, Min Elevation: {min_el:.2f}°")
    print(f"Max Zenith: {max_zenith:.2f}°, Min Zenith: {min_zenith:.2f}°")

    # Plotting
    plt.figure(figsize=(15, 4))  # Adjust the figure size for screen fit

    # Plot azimuth
    plt.subplot(1, 3, 1)
    plt.plot(hours, azimuths, label='Azimuth', color='orange')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Azimuth (degrees)')
    plt.title('Sun Azimuth Throughout the Day')
    plt.grid(True)
    plt.annotate(f'Max: {max_az:.2f}°', xy=(hours[np.argmax(azimuths)], max_az), xytext=(10, max_az+10),
                 arrowprops=dict(arrowstyle='->', color='black'))
    plt.annotate(f'Min: {min_az:.2f}°', xy=(hours[np.argmin(azimuths)], min_az), xytext=(10, min_az-10),
                 arrowprops=dict(arrowstyle='->', color='black'))

    # Plot elevation
    plt.subplot(1, 3, 2)
    plt.plot(hours, elevations, label='Elevation', color='blue')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Elevation (degrees)')
    plt.title('Sun Elevation Throughout the Day')
    plt.grid(True)
    plt.annotate(f'Max: {max_el:.2f}°', xy=(hours[np.argmax(elevations)], max_el), xytext=(10, max_el+5),
                 arrowprops=dict(arrowstyle='->', color='black'))
    plt.annotate(f'Min: {min_el:.2f}°', xy=(hours[np.argmin(elevations)], min_el), xytext=(10, min_el-5),
                 arrowprops=dict(arrowstyle='->', color='black'))

    # Plot zenith angle
    plt.subplot(1, 3, 3)
    plt.plot(hours, zeniths, label='Zenith', color='green')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Zenith Angle (degrees)')
    plt.title('Sun Zenith Angle Throughout the Day')
    plt.grid(True)
    plt.annotate(f'Max: {max_zenith:.2f}°', xy=(hours[np.argmax(zeniths)], max_zenith), xytext=(10, max_zenith+5),
                 arrowprops=dict(arrowstyle='->', color='black'))
    plt.annotate(f'Min: {min_zenith:.2f}°', xy=(hours[np.argmin(zeniths)], min_zenith), xytext=(10, min_zenith-5),
                 arrowprops=dict(arrowstyle='->', color='black'))

    plt.tight_layout()
    plt.show()

# Call the function for a specific date and location
plot_sun_path(2025, 6, 20, lat=43.5, long=-80.5)
