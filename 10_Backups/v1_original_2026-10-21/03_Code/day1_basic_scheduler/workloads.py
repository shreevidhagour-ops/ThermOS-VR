from process import Process


def create_vr_workload():
    processes = [
        Process(
            pid=1,
            name="Frame Rendering",
            arrival_time=0,
            burst_time=8,
            priority=1,
            workload_intensity=90,
            task_type="Rendering",
            deadline=10
        ),

        Process(
            pid=2,
            name="Motion Tracking",
            arrival_time=1,
            burst_time=4,
            priority=2,
            workload_intensity=70,
            task_type="Tracking",
            deadline=8
        ),

        Process(
            pid=3,
            name="Physics Engine",
            arrival_time=2,
            burst_time=6,
            priority=3,
            workload_intensity=80,
            task_type="Physics",
            deadline=12
        ),

        Process(
            pid=4,
            name="Sensor Processing",
            arrival_time=3,
            burst_time=3,
            priority=2,
            workload_intensity=60,
            task_type="Sensor",
            deadline=10
        ),

        Process(
            pid=5,
            name="Audio",
            arrival_time=4,
            burst_time=2,
            priority=4,
            workload_intensity=30,
            task_type="Audio",
            deadline=12
        ),

        Process(
            pid=6,
            name="Background",
            arrival_time=5,
            burst_time=5,
            priority=5,
            workload_intensity=20,
            task_type="Background",
            deadline=20
        )
    ]

    return processes

def create_thermal_stress_workload():
    """
    Create a sustained high-intensity AR/VR workload
    for evaluating thermal-aware scheduling.
    """

    processes = [
        Process(
            pid=1,
            name="High-Load Rendering",
            arrival_time=0,
            burst_time=20,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=22
        ),

        Process(
            pid=2,
            name="Advanced Physics",
            arrival_time=0,
            burst_time=18,
            priority=2,
            workload_intensity=95,
            task_type="Physics",
            deadline=25
        ),

        Process(
            pid=3,
            name="Motion Tracking",
            arrival_time=1,
            burst_time=15,
            priority=1,
            workload_intensity=90,
            task_type="Tracking",
            deadline=20
        ),

        Process(
            pid=4,
            name="Sensor Processing",
            arrival_time=2,
            burst_time=12,
            priority=2,
            workload_intensity=85,
            task_type="Sensor",
            deadline=18
        ),

        Process(
            pid=5,
            name="Audio Processing",
            arrival_time=3,
            burst_time=8,
            priority=3,
            workload_intensity=60,
            task_type="Audio",
            deadline=20
        ),

        Process(
            pid=6,
            name="Background Compute",
            arrival_time=4,
            burst_time=10,
            priority=5,
            workload_intensity=50,
            task_type="Background",
            deadline=30
        )
    ]

    return processes

def create_burst_vr_workload():
    """
    Create a burst-oriented AR/VR workload representing
    a sudden increase in rendering and computational demand.
    """

    processes = [
        Process(
            pid=1,
            name="Initial Rendering",
            arrival_time=0,
            burst_time=8,
            priority=1,
            workload_intensity=95,
            task_type="Rendering",
            deadline=10
        ),

        Process(
            pid=2,
            name="Initial Physics",
            arrival_time=0,
            burst_time=8,
            priority=2,
            workload_intensity=90,
            task_type="Physics",
            deadline=12
        ),

        Process(
            pid=3,
            name="Burst Rendering",
            arrival_time=8,
            burst_time=15,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=22
        ),

        Process(
            pid=4,
            name="Burst Physics",
            arrival_time=8,
            burst_time=14,
            priority=2,
            workload_intensity=95,
            task_type="Physics",
            deadline=24
        ),

        Process(
            pid=5,
            name="Motion Tracking",
            arrival_time=9,
            burst_time=10,
            priority=1,
            workload_intensity=85,
            task_type="Tracking",
            deadline=20
        ),

        Process(
            pid=6,
            name="Sensor Burst",
            arrival_time=10,
            burst_time=8,
            priority=2,
            workload_intensity=80,
            task_type="Sensor",
            deadline=21
        )
    ]

    return processes

def create_sustained_thermal_workload():
    """
    Create a long-duration, high-intensity AR/VR workload
    for evaluating thermal-aware scheduling.

    This scenario is designed to sustain computational
    pressure long enough for the thermal model to enter
    higher thermal states.
    """

    processes = [

        Process(
            pid=1,
            name="Sustained Rendering",
            arrival_time=0,
            burst_time=50,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=55
        ),

        Process(
            pid=2,
            name="Sustained Physics",
            arrival_time=0,
            burst_time=50,
            priority=2,
            workload_intensity=95,
            task_type="Physics",
            deadline=58
        ),

        Process(
            pid=3,
            name="Continuous Tracking",
            arrival_time=0,
            burst_time=45,
            priority=1,
            workload_intensity=90,
            task_type="Tracking",
            deadline=55
        ),

        Process(
            pid=4,
            name="Continuous Sensor Processing",
            arrival_time=0,
            burst_time=40,
            priority=2,
            workload_intensity=85,
            task_type="Sensor",
            deadline=55
        ),

        Process(
            pid=5,
            name="Audio Processing",
            arrival_time=5,
            burst_time=30,
            priority=3,
            workload_intensity=60,
            task_type="Audio",
            deadline=45
        ),

        Process(
            pid=6,
            name="Background Compute",
            arrival_time=10,
            burst_time=30,
            priority=5,
            workload_intensity=50,
            task_type="Background",
            deadline=60
        )
    ]

    return processes

def create_hot_thermal_workload():
    """
    Create a very long, high-intensity AR/VR workload
    designed to push the simulated cores into the HOT
    thermal state.

    This workload is used to evaluate thermal-aware
    scheduling and DVFS under sustained thermal pressure.
    """

    processes = [

        Process(
            pid=1,
            name="Extreme Rendering",
            arrival_time=0,
            burst_time=80,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=90
        ),

        Process(
            pid=2,
            name="Extreme Physics",
            arrival_time=0,
            burst_time=80,
            priority=1,
            workload_intensity=100,
            task_type="Physics",
            deadline=95
        ),

        Process(
            pid=3,
            name="Continuous Tracking",
            arrival_time=0,
            burst_time=75,
            priority=1,
            workload_intensity=95,
            task_type="Tracking",
            deadline=90
        ),

        Process(
            pid=4,
            name="Heavy Sensor Processing",
            arrival_time=0,
            burst_time=70,
            priority=2,
            workload_intensity=90,
            task_type="Sensor",
            deadline=90
        ),

        Process(
            pid=5,
            name="Audio Processing",
            arrival_time=10,
            burst_time=50,
            priority=3,
            workload_intensity=70,
            task_type="Audio",
            deadline=75
        ),

        Process(
            pid=6,
            name="Background Compute",
            arrival_time=20,
            burst_time=50,
            priority=5,
            workload_intensity=60,
            task_type="Background",
            deadline=100
        )
    ]

    return processes

def create_heterogeneous_thermal_workload():
    """
    Create a mixed-intensity AR/VR workload designed to
    evaluate heterogeneous core selection.

    Heavy real-time tasks should favor the Performance core,
    while lighter tasks can be handled by the Efficiency core.
    """

    processes = [

        Process(
            pid=1,
            name="VR Frame Rendering",
            arrival_time=0,
            burst_time=50,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=60
        ),

        Process(
            pid=2,
            name="VR Physics",
            arrival_time=0,
            burst_time=45,
            priority=1,
            workload_intensity=90,
            task_type="Physics",
            deadline=65
        ),

        Process(
            pid=3,
            name="Motion Tracking",
            arrival_time=5,
            burst_time=35,
            priority=2,
            workload_intensity=70,
            task_type="Tracking",
            deadline=55
        ),

        Process(
            pid=4,
            name="Sensor Processing",
            arrival_time=8,
            burst_time=30,
            priority=2,
            workload_intensity=55,
            task_type="Sensor",
            deadline=60
        ),

        Process(
            pid=5,
            name="Audio Processing",
            arrival_time=10,
            burst_time=25,
            priority=3,
            workload_intensity=35,
            task_type="Audio",
            deadline=55
        ),

        Process(
            pid=6,
            name="Background Task",
            arrival_time=15,
            burst_time=30,
            priority=5,
            workload_intensity=20,
            task_type="Background",
            deadline=100
        )
    ]

    return processes

def create_thermal_imbalance_workload():
    """
    Create an AR/VR workload designed to create thermal
    imbalance between the two heterogeneous cores.

    A sustained high-intensity rendering task is followed
    by additional tasks arriving later. This gives the
    thermal-aware scheduler an opportunity to prefer the
    cooler core.
    """

    processes = [

        Process(
            pid=1,
            name="Sustained VR Rendering",
            arrival_time=0,
            burst_time=70,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=90
        ),

        Process(
            pid=2,
            name="VR Physics",
            arrival_time=0,
            burst_time=60,
            priority=1,
            workload_intensity=90,
            task_type="Physics",
            deadline=85
        ),

        Process(
            pid=3,
            name="Late Motion Tracking",
            arrival_time=35,
            burst_time=25,
            priority=1,
            workload_intensity=80,
            task_type="Tracking",
            deadline=70
        ),

        Process(
            pid=4,
            name="Late Sensor Processing",
            arrival_time=40,
            burst_time=25,
            priority=2,
            workload_intensity=60,
            task_type="Sensor",
            deadline=75
        ),

        Process(
            pid=5,
            name="Audio Processing",
            arrival_time=45,
            burst_time=20,
            priority=3,
            workload_intensity=35,
            task_type="Audio",
            deadline=80
        ),

        Process(
            pid=6,
            name="Background Compute",
            arrival_time=50,
            burst_time=25,
            priority=5,
            workload_intensity=20,
            task_type="Background",
            deadline=100
        )
    ]

    return processes
