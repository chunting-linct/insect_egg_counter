from egg_counter.pi_hardware import PiHardware


def test_add_one():
    pi_hardware = PiHardware()
    pi_hardware.x_neg_boundary= -1
    pi_hardware.y_neg_boundary= -1
    pi_hardware.x_pos_boundary= 50
    pi_hardware.y_pos_boundary= 40
    
    x_step, y_step = pi_hardware.calculate_step_list()
    assert x_step == [50, 50]
    assert y_step == [50]
