from opentrons import protocol_api
import string

# metadata
metadata = {
    'protocolName': 'Hybridization capture protocol',
    'author': 'Tomasz Suchan <t.suchan@botany.pl>',
    'description': 'Protocol hyRAD sequence capture',
    'apiLevel': '2.7'
}


def run(protocol: protocol_api.ProtocolContext):
    # NUMBER OF SAMPLES:
    nsamples = 8 #from 1 to 8 samples are supported

    samplerows = list(string.ascii_uppercase[0:nsamples])
    wells_wash_buffer_1 = [row + '7' for row in samplerows]
    wells_wash_buffer_2 = [row + '8' for row in samplerows] + [row + '9' for row in samplerows] + [row + '10' for row in samplerows]
    wells_elution_buffer = [row + '11' for row in samplerows]
    wells_beads = [row + '12' for row in samplerows]

    # modules
    module_pcr = protocol.load_module('thermocycler', 7)
    pcr = module_pcr.load_labware('biorad_96_wellplate_200ul_pcr')

    module_magnet = protocol.load_module('magdeck', 4)
    magnet = module_magnet.load_labware('biorad_96_wellplate_200ul_pcr')

    # labware
    tiprack_200 = [protocol.load_labware('opentrons_96_filtertiprack_200ul', slot) for slot in ["1","5"]]
    tiprack_1000 = protocol.load_labware('opentrons_96_filtertiprack_1000ul', 6)
    trash = protocol.load_labware('agilent_1_reservoir_290ml', 9)
    tubes_rack_l = protocol.load_labware('opentrons_6_tuberack_falcon_50ml_conical', 2)
    tubes_rack_s = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 3)

    # pipettes
    pipette_multi = protocol.load_instrument('p300_multi', 'left', tip_racks=tiprack_200)
    pipette_single = protocol.load_instrument('p1000_single', 'right', tip_racks=[tiprack_1000])
    pipette_single.default_speed = 100

    # commands
    protocol.pause('Load the samples with blocking mix in column 2 on the PCR and pres resume.')
    module_pcr.close_lid()
    module_pcr.set_lid_temperature(95)
    module_pcr.set_block_temperature(95)
    protocol.delay(minutes=5)
    module_pcr.set_block_temperature(55)
    module_pcr.open_lid()
    protocol.pause('Load hybridization mix in column 1 on the PCR and pres resume.')
    module_pcr.close_lid()
    protocol.delay(minutes=5)
    module_pcr.open_lid()
    pipette_multi.transfer(18, pcr.columns_by_name()['1'],
                           pcr.columns_by_name()['2'],
                           mix_after=(5, 15))
    module_pcr.close_lid()

    protocol.pause('Incubation started, resume after the required amount of time. Beforre resuming, place reagents on racks: in falcon tubes (A1 - wash 1, A2 - wash 2), and 1.5 ml tubes (A1 - elution buffer, A2 - dynabeads). Then press resume to start.')
    module_pcr.open_lid()
    pipette_single.distribute(130,
                              tubes_rack_l.wells_by_name()['A1'],
                              [pcr.wells_by_name()[well_name] for well_name in wells_wash_buffer_1],
                              disposal_volume=25)  # wash buffer1
    pipette_single.distribute(130,
                              tubes_rack_l.wells_by_name()['A2'],
                              [pcr.wells_by_name()[well_name] for well_name in wells_wash_buffer_2],
                              disposal_volume=25)  # wash buffer2
    pipette_single.distribute(40,
                              tubes_rack_s.wells_by_name()['A1'],
                              [pcr.wells_by_name()[well_name] for well_name in wells_elution_buffer],
                              disposal_volume=25) # elution buffer
    pipette_single.distribute(75,
                              tubes_rack_s.wells_by_name()['A2'],
                              [pcr.wells_by_name()[well_name] for well_name in wells_beads],
                              mix_before=(5, 75*nsamples/2),
                              disposal_volume=10,
                              touch_tip=True) # dynabeads

    protocol.pause("Check if everything is OK and pres resume.")
    module_pcr.close_lid()
    protocol.delay(minutes=5)
    module_pcr.open_lid()
    pipette_multi.transfer(70, pcr.columns_by_name()['12'],
                           pcr.columns_by_name()['2'],
                           mix_before=(5, 60),
                           mix_after=(5, 60))
    for _ in range(5):
        module_pcr.close_lid()
        protocol.delay(minutes=4)
        module_pcr.open_lid()
        pipette_multi.pick_up_tip()
        pipette_multi.mix(5, 50, pcr.wells_by_name()["A2"])
        pipette_multi.drop_tip()
    module_pcr.close_lid()
    protocol.delay(minutes=5)
    module_pcr.open_lid()

    def wash(step, time, vol_in, vol_out):
        module_pcr.open_lid()
        pipette_multi.pick_up_tip()
        pipette_multi.transfer(vol_in, pcr.columns()[1],
                               magnet.columns()[1],
                               aspirate_speed=50,
                               new_tip='never',
                               mix_before=(5, 90))
        module_magnet.engage()
        protocol.delay(seconds=30)
        pipette_multi.transfer(vol_out, magnet.columns()[1],
                               trash.columns()[0],
                               new_tip='never')
        pipette_multi.drop_tip()
        module_magnet.disengage()
        pipette_multi.pick_up_tip()
        pipette_multi.transfer(vol_in, pcr.columns()[step+5],
                               magnet.columns()[1],
                               new_tip='never',
                               mix_after=(5, 90))
        pipette_multi.transfer(vol_out, magnet.columns()[1],
                               pcr.columns()[1],
                               aspirate_speed=50,
                               new_tip='never')
        pipette_multi.drop_tip()
        module_pcr.close_lid()
        protocol.delay(minutes=time)

    # wash steps 1-3
    wash(step=1, time=15, vol_in=100, vol_out=150)
    for i in range(2,5):
        wash(step=i, time=10, vol_in=100, vol_out=100)

    # last wash and elute in final volume
    module_pcr.open_lid()
    pipette_multi.pick_up_tip()
    pipette_multi.transfer(100, pcr.columns()[1],
                           magnet.columns()[1],
                           aspirate_speed=50,
                           new_tip='never',
                           mix_before=(5, 90))
    module_magnet.engage()
    protocol.delay(seconds=30)
    pipette_multi.transfer(180, magnet.columns()[1],
                           trash.columns()[0],
                           new_tip='never')
    pipette_multi.drop_tip()
    module_magnet.disengage()
    pipette_multi.pick_up_tip()
    pipette_multi.transfer(30, pcr.columns()[10],
                           magnet.columns()[1],
                           aspirate_speed=50,
                           new_tip='never')
    pipette_multi.drop_tip()
    module_pcr.deactivate()
