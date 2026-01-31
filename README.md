# EV3 Pizza Delivery Robot

Autonomous pizza delivery system built with LEGO Mindstorms EV3. The robot navigates a circuit by following a black line, interprets traffic light sequences to determine delivery points, and avoids obstacles using ultrasonic sensing.

## Project Overview

This project was developed for the Robotics and Advanced Control (RKA) course at EHU. The robot simulates a pizza delivery scenario where it must:

1. Follow a black line circuit
2. Read traffic light color sequences (RGB) to identify delivery points
3. Take the correct exit based on a predefined delivery code
4. Avoid collisions with other robots on the circuit

## Hardware Configuration

| Component | Position | Function |
|-----------|----------|----------|
| LSA Sensor (8-channel) | Front, close to ground | Black line detection |
| Color Sensor | Front-right | Traffic light RGB reading |
| Ultrasonic Sensor | Front, elevated | Obstacle detection (30cm threshold) |
| 2x Large Motors | Ports A and D | Differential drive |

## Software Architecture

The system is decomposed into three concurrent behaviors managed through Python threading:

### 1. Line Following

Uses an 8-channel LSA sensor to detect the black line position:

- Calculates average sensor value as threshold
- Identifies line segments and computes center index
- Applies proportional correction based on deviation from robot center (3.5)
```python
deviation = 3.5 - center_index
v_left = base_speed - deviation * k
v_right = base_speed + deviation * k
```

### 2. Traffic Light Interpretation (Threaded)

The `semaforoa` class runs in a separate thread continuously monitoring RGB values:

- Compares readings against predefined color references
- Filters ground readings using difference threshold (>90)
- Builds 3-color sequences and validates against delivery code
- Sets `atera` flag when correct sequence detected

### 3. Obstacle Avoidance (Threaded)

The `ultrasonic` class runs in a separate thread:

- Continuously monitors distance to nearest object
- Stops robot when obstacle detected within 30cm
- LED indicators: RED (stopped), GREEN (moving)

## Control Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `t_handia` | 6 | Strong correction factor for large deviations |
| `t_txikia` | 1 | Gentle correction factor for small deviations |
| `base_speed` | 20 | Base motor speed |
| `obstacle_threshold` | 30 cm | Distance to trigger stop |

## Delivery Code Format

The delivery sequence is defined as color-position pairs:
```python
color_sequence = ['blue', 'green', 'green']
position_sequence = [3, 3, 1]
```

Interpretation:
- 1st delivery: Exit at traffic light with BLUE in 3rd position
- 2nd delivery: Exit at traffic light with GREEN in 3rd position
- 3rd delivery: Exit at traffic light with GREEN in 1st position

## Results

| Metric | Value |
|--------|-------|
| Success Rate | 80% (4/5 laps completed) |
| Average Lap Time | 1 min 24 sec |
| Obstacle Detection Range | 30 cm |

## Project Structure
```
ev3-pizza-delivery/
├── README.md
├── src/
│   └── pizza_delivery.py
├── docs/
│   └── report.pdf
└── assets/
    └── robot.jpg
```

## Requirements

- LEGO Mindstorms EV3 with ev3dev OS
- Python 3
- ev3dev2 library

## Usage

Upload to EV3 brick and run:
```bash
python3 pizza_delivery.py
```

To modify the delivery route, edit the sequence parameters:
```python
parametroKolore = ['blue', 'green', 'green']
parametroZenbaki = [3, 3, 1]
```

## Known Issues and Potential Improvements

### Current Limitations

1. **Color calibration**: Lighting conditions affect RGB readings, requiring manual calibration
2. **Sharp curves**: Robot occasionally loses line on tight turns
3. **Sensor interference**: Occasional conflicts between ultrasonic and color sensor readings

### Proposed Improvements

1. PID control for smoother line following
2. Dynamic color calibration adapting to lighting conditions
3. Pre-loaded circuit map for optimized navigation
4. Additional infrared sensors for improved obstacle detection

## Course

Robotics and Advanced Control (Robotika eta Kontrol Adimendua) EHU
