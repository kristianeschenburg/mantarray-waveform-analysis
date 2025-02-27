# -*- coding: utf-8 -*-
import math
import os

from mantarray_waveform_analysis import AMPLITUDE_UUID
from mantarray_waveform_analysis import AUC_UUID
from mantarray_waveform_analysis import CONTRACTION_VELOCITY_UUID
from mantarray_waveform_analysis import find_twitch_indices
from mantarray_waveform_analysis import IRREGULARITY_INTERVAL_UUID
from mantarray_waveform_analysis import MIN_NUMBER_PEAKS
from mantarray_waveform_analysis import MIN_NUMBER_VALLEYS
from mantarray_waveform_analysis import peak_detector
from mantarray_waveform_analysis import PRIOR_PEAK_INDEX_UUID
from mantarray_waveform_analysis import PRIOR_VALLEY_INDEX_UUID
from mantarray_waveform_analysis import RELAXATION_VELOCITY_UUID
from mantarray_waveform_analysis import SUBSEQUENT_PEAK_INDEX_UUID
from mantarray_waveform_analysis import SUBSEQUENT_VALLEY_INDEX_UUID
from mantarray_waveform_analysis import TooFewPeaksDetectedError
from mantarray_waveform_analysis import TWITCH_FREQUENCY_UUID
from mantarray_waveform_analysis import TWITCH_PERIOD_UUID
from mantarray_waveform_analysis import TwoPeaksInARowError
from mantarray_waveform_analysis import TwoValleysInARowError
from mantarray_waveform_analysis import WIDTH_FALLING_COORDS_UUID
from mantarray_waveform_analysis import WIDTH_RISING_COORDS_UUID
from mantarray_waveform_analysis import WIDTH_UUID
from mantarray_waveform_analysis import WIDTH_VALUE_UUID
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from pytest import approx

from .fixtures_compression import fixture_new_A1
from .fixtures_compression import fixture_new_A2
from .fixtures_compression import fixture_new_A3
from .fixtures_compression import fixture_new_A4
from .fixtures_compression import fixture_new_A5
from .fixtures_compression import fixture_new_A6
from .fixtures_peak_detection import fixture_MA20123123__2020_10_13_173812__B6
from .fixtures_peak_detection import fixture_MA20123123__2020_10_13_234733__A1
from .fixtures_peak_detection import fixture_MA20123456__2020_08_17_145752__A1
from .fixtures_peak_detection import fixture_MA202000030__2020_12_11_233215__D4
from .fixtures_peak_detection import fixture_MA202000127__2021_03_26_174059__A3
from .fixtures_peak_detection import fixture_MA202000127__2021_04_20_212922__A3
from .fixtures_peak_detection import fixture_maiden_voyage_data
from .fixtures_peak_detection import fixture_noisy_data_A1
from .fixtures_peak_detection import fixture_noisy_data_B1
from .fixtures_utils import _get_data_metrics
from .fixtures_utils import _get_unrounded_data_metrics
from .fixtures_utils import _load_file_tsv
from .fixtures_utils import _plot_data
from .fixtures_utils import assert_percent_diff
from .fixtures_utils import create_numpy_array_of_raw_gmr_from_python_arrays
from .fixtures_utils import PATH_TO_DATASETS
from .fixtures_utils import PATH_TO_PNGS

matplotlib.use("Agg")


__fixtures__ = [
    fixture_maiden_voyage_data,
    fixture_new_A1,
    fixture_new_A2,
    fixture_new_A3,
    fixture_new_A4,
    fixture_new_A5,
    fixture_new_A6,
    fixture_noisy_data_A1,
    fixture_noisy_data_B1,
    fixture_MA20123123__2020_10_13_173812__B6,
    fixture_MA20123123__2020_10_13_234733__A1,
    fixture_MA202000030__2020_12_11_233215__D4,
    fixture_MA202000127__2021_03_26_174059__A3,
    fixture_MA202000127__2021_04_20_212922__A3,
    fixture_MA20123456__2020_08_17_145752__A1,
]


def _plot_twitch_widths(filtered_data, per_twitch_dict, my_local_path_graphs):
    # plot and save results
    plt.figure()
    plt.plot(filtered_data[0, :], filtered_data[1, :])
    label_made = False
    for twitch in per_twitch_dict:
        percent_dict = per_twitch_dict[twitch][WIDTH_UUID]
        clrs = [
            "k",
            "r",
            "g",
            "b",
            "c",
            "m",
            "y",
            "k",
            "darkred",
            "darkgreen",
            "darkblue",
            "darkcyan",
            "darkmagenta",
            "orange",
            "gray",
            "lime",
            "crimson",
            "yellow",
        ]
        count = 0
        for percent in reversed(list(percent_dict.keys())):
            rising_x = percent_dict[percent][WIDTH_RISING_COORDS_UUID][0]
            falling_x = percent_dict[percent][WIDTH_FALLING_COORDS_UUID][0]
            if not label_made:
                plt.plot(
                    rising_x,
                    percent_dict[percent][WIDTH_RISING_COORDS_UUID][1],
                    "o",
                    color=clrs[count],
                    label=percent,
                )
                plt.plot(
                    falling_x,
                    percent_dict[percent][WIDTH_FALLING_COORDS_UUID][1],
                    "o",
                    color=clrs[count],
                )
            else:
                plt.plot(
                    rising_x,
                    percent_dict[percent][WIDTH_RISING_COORDS_UUID][1],
                    "o",
                    color=clrs[count],
                )
                plt.plot(
                    falling_x,
                    percent_dict[percent][WIDTH_FALLING_COORDS_UUID][1],
                    "o",
                    color=clrs[count],
                )
            count += 1
            if count > 16:
                label_made = True
    plt.legend(loc="best")
    plt.xlabel("Time (centimilliseconds)")
    plt.ylabel("Voltage (V)")
    plt.savefig(my_local_path_graphs)


def test_new_A1_period(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 11
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"] == approx(80182, rel=1e-5)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 1696)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 78000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 84000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[105000][TWITCH_PERIOD_UUID] == 81000
    assert per_twitch_dict[186000][TWITCH_PERIOD_UUID] == 80000
    assert per_twitch_dict[266000][TWITCH_PERIOD_UUID] == 78000


def test_new_A1_frequency(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    assert aggregate_metrics_dict[TWITCH_FREQUENCY_UUID]["mean"] == approx(1.2477183310516644)
    assert aggregate_metrics_dict[TWITCH_FREQUENCY_UUID]["std"] == approx(0.026146910973044845)
    assert per_twitch_dict[105000][TWITCH_FREQUENCY_UUID] == approx(1.2345679)


def test_new_A2_period(new_A2):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A2)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 80182)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 2289)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 77000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 85000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[104000][TWITCH_PERIOD_UUID] == 81000
    assert per_twitch_dict[185000][TWITCH_PERIOD_UUID] == 77000
    assert per_twitch_dict[262000][TWITCH_PERIOD_UUID] == 85000


def test_new_A3_period(new_A3):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A3)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 80182)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 4600)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 73000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 85000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[108000][TWITCH_PERIOD_UUID] == 85000
    assert per_twitch_dict[193000][TWITCH_PERIOD_UUID] == 73000
    assert per_twitch_dict[266000][TWITCH_PERIOD_UUID] == 85000


def test_new_A4_period(new_A4):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A4)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 57667)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 1247)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 56000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 59000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[81000][TWITCH_PERIOD_UUID] == 56000
    assert per_twitch_dict[137000][TWITCH_PERIOD_UUID] == 59000
    assert per_twitch_dict[196000][TWITCH_PERIOD_UUID] == 59000


def test_new_A5_period(new_A5):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A5)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 58000)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 1265)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 55000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 59000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[80000][TWITCH_PERIOD_UUID] == 58000
    assert per_twitch_dict[138000][TWITCH_PERIOD_UUID] == 59000
    assert per_twitch_dict[197000][TWITCH_PERIOD_UUID] == 58000


def test_new_A6_period(new_A6):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A6)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 57667)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 4922)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 48000
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 66000
    # test data_metrics per beat dictionary
    assert per_twitch_dict[88000][TWITCH_PERIOD_UUID] == 60000
    assert per_twitch_dict[148000][TWITCH_PERIOD_UUID] == 53000
    assert per_twitch_dict[201000][TWITCH_PERIOD_UUID] == 54000


def test_maiden_voyage_data_period(maiden_voyage_data):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(maiden_voyage_data)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["mean"], 81400)
    assert_percent_diff(aggregate_metrics_dict[TWITCH_PERIOD_UUID]["std"], 1480)
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["min"] == 78500
    assert aggregate_metrics_dict[TWITCH_PERIOD_UUID]["max"] == 83500

    # test data_metrics per beat dictionary
    assert per_twitch_dict[123500][TWITCH_PERIOD_UUID] == 83000
    assert per_twitch_dict[449500][TWITCH_PERIOD_UUID] == 80000
    assert per_twitch_dict[856000][TWITCH_PERIOD_UUID] == 81500


def test_new_A1_contraction_velocity(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[105000][CONTRACTION_VELOCITY_UUID], 6.474188398084087)
    assert_percent_diff(per_twitch_dict[186000][CONTRACTION_VELOCITY_UUID], 5.99059)
    assert_percent_diff(per_twitch_dict[266000][CONTRACTION_VELOCITY_UUID], 6.800115874855156)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[CONTRACTION_VELOCITY_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[CONTRACTION_VELOCITY_UUID]["mean"], 6.440001805351568)
    assert_percent_diff(aggregate_metrics_dict[CONTRACTION_VELOCITY_UUID]["std"], 0.2531719477692566)
    assert_percent_diff(aggregate_metrics_dict[CONTRACTION_VELOCITY_UUID]["min"], 5.990590432409137)
    assert_percent_diff(aggregate_metrics_dict[CONTRACTION_VELOCITY_UUID]["max"], 6.905701940184699)


def test_new_A1_relaxation_velocity(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[105000][RELAXATION_VELOCITY_UUID], 3.8382997965182004)
    assert_percent_diff(per_twitch_dict[186000][RELAXATION_VELOCITY_UUID], 3.7836936936936936)
    assert_percent_diff(per_twitch_dict[266000][RELAXATION_VELOCITY_UUID], 4.144501085146116)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[RELAXATION_VELOCITY_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[RELAXATION_VELOCITY_UUID]["mean"], 4.053570198234518)
    assert_percent_diff(aggregate_metrics_dict[RELAXATION_VELOCITY_UUID]["std"], 0.23419699561645954)
    assert_percent_diff(aggregate_metrics_dict[RELAXATION_VELOCITY_UUID]["min"], 3.7407880918679512)
    assert_percent_diff(aggregate_metrics_dict[RELAXATION_VELOCITY_UUID]["max"], 4.495471014492754)


def test_new_A1_interval_irregularity(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics per beat dictionary
    assert math.isnan(per_twitch_dict[105000][IRREGULARITY_INTERVAL_UUID]) is True
    assert per_twitch_dict[186000][IRREGULARITY_INTERVAL_UUID] == 1000.0
    assert math.isnan(per_twitch_dict[906000][IRREGULARITY_INTERVAL_UUID]) is True

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["mean"], 2444.444)
    assert_percent_diff(aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["std"], 1422.916)
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["min"] == 1000.0
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["max"] == 6000.0


def test_new_two_twitches_interval_irregularity(MA20123456__2020_08_17_145752__A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(MA20123456__2020_08_17_145752__A1)

    # test data_metrics per beat dictionary
    assert math.isnan(per_twitch_dict[108160][IRREGULARITY_INTERVAL_UUID]) is True
    assert math.isnan(per_twitch_dict[208000][IRREGULARITY_INTERVAL_UUID]) is True

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["n"] == 2
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["mean"] is None
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["std"] is None
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["min"] is None
    assert aggregate_metrics_dict[IRREGULARITY_INTERVAL_UUID]["max"] is None


def test_new_A1_amplitude(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 103286)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 1855)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 100953
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 106274

    # test data_metrics per beat dictionary
    assert per_twitch_dict[105000][AMPLITUDE_UUID] == 106274
    assert per_twitch_dict[186000][AMPLITUDE_UUID] == 104624
    assert per_twitch_dict[266000][AMPLITUDE_UUID] == 102671


def test_new_A1_amplitude_unrounded(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_unrounded_data_metrics(new_A1)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 11
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["mean"] == approx(103286.4090)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["std"] == approx(1855.4460)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == approx(100953)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == approx(106274.5)

    # test data_metrics per beat dictionary
    assert per_twitch_dict[105000][AMPLITUDE_UUID] == approx(106274.5)
    assert per_twitch_dict[186000][AMPLITUDE_UUID] == approx(104624.5)
    assert per_twitch_dict[266000][AMPLITUDE_UUID] == approx(102671)


def test_new_A2_amplitude(new_A2):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A2)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 95231)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 1731)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 92662
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 98873

    # test data_metrics per beat dictionary
    assert per_twitch_dict[104000][AMPLITUDE_UUID] == 93844
    assert per_twitch_dict[185000][AMPLITUDE_UUID] == 95950
    assert per_twitch_dict[262000][AMPLITUDE_UUID] == 98873


def test_new_A3_amplitude(new_A3):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A3)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 70491)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 2136)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 67811
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 73363

    # test data_metrics per beat dictionary
    assert per_twitch_dict[108000][AMPLITUDE_UUID] == 67811
    assert per_twitch_dict[193000][AMPLITUDE_UUID] == 73363
    assert per_twitch_dict[266000][AMPLITUDE_UUID] == 67866


def test_new_A4_amplitude(new_A4):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A4)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 130440)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 3416)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 124836
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 136096

    # test data_metrics per beat dictionary
    assert per_twitch_dict[81000][AMPLITUDE_UUID] == 131976
    assert per_twitch_dict[137000][AMPLITUDE_UUID] == 136096
    assert per_twitch_dict[196000][AMPLITUDE_UUID] == 129957


def test_new_A5_amplitude(new_A5):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A5)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 55863)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 1144)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 54291
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 58845

    # test data_metrics per beat dictionary
    assert per_twitch_dict[80000][AMPLITUDE_UUID] == 54540
    assert per_twitch_dict[138000][AMPLITUDE_UUID] == 54739
    assert per_twitch_dict[197000][AMPLITUDE_UUID] == 56341


def test_new_A6_amplitude(new_A6):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A6)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 10265)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 568)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 9056
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 11052

    # test data_metrics per beat dictionary
    assert per_twitch_dict[88000][AMPLITUDE_UUID] == 10761
    assert per_twitch_dict[148000][AMPLITUDE_UUID] == 10486
    assert per_twitch_dict[201000][AMPLITUDE_UUID] == 10348


def test_maiden_voyage_data_amplitude(maiden_voyage_data):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(maiden_voyage_data)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["mean"], 477098)
    assert_percent_diff(aggregate_metrics_dict[AMPLITUDE_UUID]["std"], 40338)
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["min"] == 416896
    assert aggregate_metrics_dict[AMPLITUDE_UUID]["max"] == 531133

    # test data_metrics per beat dictionary
    assert per_twitch_dict[123500][AMPLITUDE_UUID] == 523198
    assert per_twitch_dict[449500][AMPLITUDE_UUID] == 435673
    assert per_twitch_dict[856000][AMPLITUDE_UUID] == 464154


def test_new_A1_twitch_widths_unrounded(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_unrounded_data_metrics(new_A1)

    assert per_twitch_dict[105000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == approx(10768.4501)

    assert per_twitch_dict[186000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == approx(25339.5298)
    assert per_twitch_dict[266000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == approx(43565.8953)

    assert per_twitch_dict[105000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID][0] == approx(109494.2651)
    assert per_twitch_dict[105000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID][1] == approx(-211000.4)

    assert per_twitch_dict[186000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID][0] == approx(171481.9239)
    assert per_twitch_dict[186000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID][1] == approx(-167630.5)

    assert aggregate_metrics_dict[WIDTH_UUID][20]["mean"] == approx(15757.7783)
    assert aggregate_metrics_dict[WIDTH_UUID][50]["std"] == approx(421.3576)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == approx(35533.5074)
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == approx(46182.3018)


def test_new_A1_twitch_widths(new_A1):
    pipeline, _ = new_A1
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A1_widths.png"))

    assert per_twitch_dict[105000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 10768
    assert per_twitch_dict[186000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 25340
    assert per_twitch_dict[266000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 43566

    assert per_twitch_dict[105000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        109494,
        -211000,
    )
    assert per_twitch_dict[186000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        171482,
        -167630,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 15758)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 422)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 35534
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 46182


def test_new_A2_twitch_widths(new_A2):
    pipeline, _ = new_A2
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A2)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A2_widths.png"))

    assert per_twitch_dict[104000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 9937
    assert per_twitch_dict[185000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 24890
    assert per_twitch_dict[262000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 43221

    assert per_twitch_dict[104000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        109092,
        -51458,
    )
    assert per_twitch_dict[185000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        171670,
        -14468,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 15343)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 377)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 35131
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 45237


def test_new_A3_twitch_widths(new_A3):
    pipeline, _ = new_A3
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A3)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A3_widths.png"))

    assert per_twitch_dict[108000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 10789
    assert per_twitch_dict[193000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 29398
    assert per_twitch_dict[266000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 46650

    assert per_twitch_dict[108000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        113846,
        233811,
    )
    assert per_twitch_dict[193000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        173960,
        258988,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 18868)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 449)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 39533
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 68356


def test_new_A4_twitch_widths(new_A4):
    pipeline, _ = new_A4
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A4)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A4_widths.png"))

    assert per_twitch_dict[81000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 8941
    assert per_twitch_dict[137000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 21595
    assert per_twitch_dict[196000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 35820

    assert per_twitch_dict[137000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        142096,
        -43120,
    )
    assert per_twitch_dict[196000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        184750,
        13350,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 13092)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 255)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 29258
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 41550


def test_new_A5_twitch_widths(new_A5):
    pipeline, _ = new_A5
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A5)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A5_widths.png"))

    assert per_twitch_dict[80000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 8051
    assert per_twitch_dict[138000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 20612
    assert per_twitch_dict[197000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 37710

    assert per_twitch_dict[138000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        143597,
        75362,
    )
    assert per_twitch_dict[197000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        186268,
        96628,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 11975)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 430)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 29683
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 44543


def test_new_A6_twitch_widths(new_A6):
    pipeline, _ = new_A6
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A6)

    # plot and save results
    _plot_twitch_widths(filtered_data, per_twitch_dict, os.path.join(PATH_TO_PNGS, "new_A6_widths.png"))

    assert per_twitch_dict[88000][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 4815
    assert per_twitch_dict[148000][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 28278
    assert per_twitch_dict[201000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 45761

    assert per_twitch_dict[148000][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        149352,
        55952,
    )
    assert per_twitch_dict[201000][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        187783,
        59651,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 10211)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 1969)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 31854
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 57570


def test_maiden_voyage_data_twitch_widths(maiden_voyage_data):
    pipeline, _ = maiden_voyage_data
    filtered_data = pipeline.get_noise_filtered_gmr()
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(maiden_voyage_data)

    # plot and save results
    _plot_twitch_widths(
        filtered_data,
        per_twitch_dict,
        os.path.join(PATH_TO_PNGS, "maiden_voyage_data_widths.png"),
    )

    assert per_twitch_dict[123500][WIDTH_UUID][10][WIDTH_VALUE_UUID] == 11711
    assert per_twitch_dict[449500][WIDTH_UUID][50][WIDTH_VALUE_UUID] == 23687
    assert per_twitch_dict[856000][WIDTH_UUID][90][WIDTH_VALUE_UUID] == 33911
    assert per_twitch_dict[123500][WIDTH_UUID][10][WIDTH_FALLING_COORDS_UUID] == (
        129431,
        301839,
    )
    assert per_twitch_dict[449500][WIDTH_UUID][50][WIDTH_RISING_COORDS_UUID] == (
        437648,
        562594,
    )

    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][20]["mean"], 16327)
    assert_percent_diff(aggregate_metrics_dict[WIDTH_UUID][50]["std"], 467)
    assert aggregate_metrics_dict[WIDTH_UUID][80]["min"] == 30252
    assert aggregate_metrics_dict[WIDTH_UUID][90]["max"] == 66476


def test_new_A1_auc(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A1)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 2197883129)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 40391699)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 2145365902)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 2268446950)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[105000][AUC_UUID], 2268446950)
    assert_percent_diff(per_twitch_dict[186000][AUC_UUID], 2203146703)
    assert_percent_diff(per_twitch_dict[266000][AUC_UUID], 2187484903)


def test_new_A1_auc_unrounded(new_A1):
    per_twitch_dict, aggregate_metrics_dict = _get_unrounded_data_metrics(new_A1)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 11
    assert aggregate_metrics_dict[AUC_UUID]["mean"] == approx(2197880868.4578)
    assert aggregate_metrics_dict[AUC_UUID]["std"] == approx(40391565.2993)
    assert aggregate_metrics_dict[AUC_UUID]["min"] == approx(2145370005.2140)
    assert aggregate_metrics_dict[AUC_UUID]["max"] == approx(2268449120.2174)

    # test data_metrics per beat dictionary
    assert per_twitch_dict[105000][AUC_UUID] == approx(2268449120.2174)
    assert per_twitch_dict[186000][AUC_UUID] == approx(2203146616.5726)
    assert per_twitch_dict[266000][AUC_UUID] == approx(2187480306.2996)


def test_new_A2_auc(new_A2):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A2)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 11
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 1979655695)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 60891061)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 1880100989)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 2098455889)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[104000][AUC_UUID], 1890483550)
    assert_percent_diff(per_twitch_dict[185000][AUC_UUID], 1995261562)
    assert_percent_diff(per_twitch_dict[262000][AUC_UUID], 2098455889)


def test_new_A3_auc(new_A3):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A3)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 1742767961)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 26476362)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 1700775183)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 1785602477)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[108000][AUC_UUID], 1743723350)
    assert_percent_diff(per_twitch_dict[193000][AUC_UUID], 1719164790)
    assert_percent_diff(per_twitch_dict[266000][AUC_UUID], 1711830854)


def test_new_A4_auc(new_A4):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A4)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 2337802567)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 85977760)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 2204456864)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 2474957390)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[81000][AUC_UUID], 2369406142)
    assert_percent_diff(per_twitch_dict[137000][AUC_UUID], 2474957390)
    assert_percent_diff(per_twitch_dict[196000][AUC_UUID], 2305482514)


def test_new_A5_auc(new_A5):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A5)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 975669720)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 39452029)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 916556595)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 1079880664)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[80000][AUC_UUID], 962568392)
    assert_percent_diff(per_twitch_dict[138000][AUC_UUID], 978169492)
    assert_percent_diff(per_twitch_dict[197000][AUC_UUID], 989808351)


def test_new_A6_auc(new_A6):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(new_A6)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 15
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 225373714)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 24559045)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 180116348)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 265573223)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[88000][AUC_UUID], 256551364)
    assert_percent_diff(per_twitch_dict[148000][AUC_UUID], 257671482)
    assert_percent_diff(per_twitch_dict[201000][AUC_UUID], 201413091)


def test_maiden_voyage_data_auc(maiden_voyage_data):
    per_twitch_dict, aggregate_metrics_dict = _get_data_metrics(maiden_voyage_data)

    # test data_metrics aggregate dictionary
    assert aggregate_metrics_dict[AUC_UUID]["n"] == 10
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["mean"], 9802421961)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["std"], 1211963395)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["min"], 8147044761)
    assert_percent_diff(aggregate_metrics_dict[AUC_UUID]["max"], 11738292588)

    # test data_metrics per beat dictionary
    assert_percent_diff(per_twitch_dict[123500][AUC_UUID], 10975158070)
    assert_percent_diff(per_twitch_dict[449500][AUC_UUID], 8678984942)
    assert_percent_diff(per_twitch_dict[856000][AUC_UUID], 8919661597)


def test_peak_detector_does_not_flip_data_by_default__because_default_kwarg_is_true():

    time, v = _load_file_tsv(os.path.join(PATH_TO_DATASETS, "new_A1_tsv.tsv"))

    # create numpy matrix
    raw_data = create_numpy_array_of_raw_gmr_from_python_arrays(time, v)
    peak_and_valley_indices = peak_detector(raw_data)
    peak_indices, valley_indices = peak_and_valley_indices

    expected_peak_indices = [70, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963]
    expected_valley_indices = [
        24,
        105,
        186,
        266,
        344,
        424,
        502,
        586,
        667,
        745,
        825,
        906,
        987,
    ]
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A1(new_A1):
    pipeline, peak_and_valley_indices = new_A1

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A1_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [70, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963]
    expected_peak_indices = [24, 105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A2(new_A2):
    pipeline, peak_and_valley_indices = new_A2

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A2_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [58, 164, 235, 308, 393, 466, 565, 643, 716, 797, 867, 947]
    expected_peak_indices = [24, 104, 185, 262, 347, 424, 505, 586, 663, 744, 825, 906, 986]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A3(new_A3):
    pipeline, peak_and_valley_indices = new_A3

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A3_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [62, 165, 239, 324, 404, 470, 562, 628, 727, 805, 871, 963]
    expected_peak_indices = [28, 108, 193, 266, 351, 428, 509, 594, 667, 752, 832, 910]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A4(new_A4):
    pipeline, peak_and_valley_indices = new_A4

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A4_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [58, 117, 176, 235, 290, 349, 407, 466, 518, 584, 639, 697, 756, 815, 867, 926, 985]
    expected_peak_indices = [23, 81, 137, 196, 255, 311, 369, 427, 486, 545, 601, 659, 715, 774, 832, 890, 946]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A5(new_A5):
    pipeline, peak_and_valley_indices = new_A5

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A5_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    expected_valley_indices = [
        62,
        121,
        180,
        232,
        294,
        345,
        411,
        463,
        522,
        584,
        640,
        694,
        753,
        805,
        871,
        930,
        989,
    ]
    expected_peak_indices = [
        25,
        80,
        138,
        197,
        255,
        311,
        370,
        428,
        487,
        545,
        601,
        660,
        718,
        777,
        836,
        891,
        950,
    ]
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_new_A6(new_A6):
    pipeline, peak_and_valley_indices = new_A6
    filtered_data = pipeline.get_noise_filtered_gmr()
    # plot and save results
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_A6_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [51, 117, 176, 238, 294, 341, 400, 459, 525, 580, 625, 698, 757, 808, 874, 926, 981]
    expected_peak_indices = [31, 88, 148, 201, 255, 318, 376, 428, 490, 552, 604, 663, 722, 784, 832, 898, 953]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_maiden_voyage_data_peak_detection(maiden_voyage_data):
    pipeline, peak_and_valley_indices = maiden_voyage_data

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "maiden_voyage_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [154, 340, 526, 686, 862, 960, 1185, 1309, 1439, 1678, 1769]
    expected_peak_indices = [84, 247, 413, 576, 739, 899, 1059, 1226, 1383, 1549, 1712, 1875]
    # fmt: on

    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_find_twitch_indices__raises_error_if_less_than_3_peaks_given():
    with pytest.raises(
        TooFewPeaksDetectedError,
        match=rf"A minimum of {MIN_NUMBER_PEAKS} peaks is required to extract twitch metrics, however only 2 peak\(s\) were detected",
    ):
        find_twitch_indices((np.array([1, 2]), None))


def test_find_twitch_indices__raises_error_if_less_than_3_valleys_given():
    with pytest.raises(
        TooFewPeaksDetectedError,
        match=rf"A minimum of {MIN_NUMBER_VALLEYS} valleys is required to extract twitch metrics, however only 2 valley\(s\) were detected",
    ):
        find_twitch_indices((np.array([1, 3, 5]), np.array([2, 4])))


def test_find_twitch_indices__raises_error_if_no_valleys_given():
    with pytest.raises(
        TooFewPeaksDetectedError,
        match=rf"A minimum of {MIN_NUMBER_VALLEYS} valleys is required to extract twitch metrics, however only 0 valley\(s\) were detected",
    ):
        find_twitch_indices((np.array([1, 3, 5]), np.array([])))


def test_find_twitch_indices__excludes_first_and_last_peak_when_no_outer_valleys(
    new_A1,
):
    _, peak_and_valley_indices = new_A1

    actual_twitch_indices = find_twitch_indices(peak_and_valley_indices)
    actual_twitch_peak_indices = list(actual_twitch_indices.keys())
    # fmt: off
    expected_twitch_peak_indices = [105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906]
    # fmt: on
    assert actual_twitch_peak_indices == expected_twitch_peak_indices

    assert actual_twitch_indices[105] == {
        PRIOR_PEAK_INDEX_UUID: 24,
        PRIOR_VALLEY_INDEX_UUID: 70,
        SUBSEQUENT_PEAK_INDEX_UUID: 186,
        SUBSEQUENT_VALLEY_INDEX_UUID: 147,
    }


def test_find_twitch_indices__excludes_only_last_peak_when_no_outer_peak_at_beginning_and_no_outer_valley_at_end(
    new_A1,
):
    _, peak_and_valley_indices = new_A1
    _, valley_indices = peak_and_valley_indices
    # fmt: off
    peak_indices = np.asarray([105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987], dtype=np.int32)
    # fmt: on
    actual_twitch_indices = find_twitch_indices((peak_indices, valley_indices))
    actual_twitch_peak_indices = list(actual_twitch_indices.keys())
    # fmt: off
    expected_twitch_peak_indices = [105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906]
    # fmt: on
    assert actual_twitch_peak_indices == expected_twitch_peak_indices

    assert actual_twitch_indices[105] == {
        PRIOR_PEAK_INDEX_UUID: None,
        PRIOR_VALLEY_INDEX_UUID: 70,
        SUBSEQUENT_PEAK_INDEX_UUID: 186,
        SUBSEQUENT_VALLEY_INDEX_UUID: 147,
    }


@pytest.mark.parametrize(
    "test_data,expected_match,test_description",
    [
        (
            [24, 69, 105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987],
            "24 and 69",
            "raises error when two peaks in a row at beginning",
        ),
        (
            [105, 186, 266, 344, 424, 502, 586, 600, 667, 745, 825, 906, 987],
            "586 and 600",
            "raises error when two peaks in a row in middle",
        ),
        (
            [105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987, 1000],
            "987 and 1000",
            "raises error when two peaks in a row at end",
        ),
    ],
)
def test_find_twitch_indices__raises_error_if_two_peaks_in_a_row__and_start_with_peak(
    new_A1, test_data, expected_match, test_description
):
    _, peak_and_valley_indices = new_A1
    _, valley_indices = peak_and_valley_indices
    peak_indices = np.asarray(test_data, dtype=np.int32)
    with pytest.raises(TwoPeaksInARowError, match=expected_match):
        find_twitch_indices((peak_indices, valley_indices))


@pytest.mark.parametrize(
    "test_data,expected_match,test_description",
    [
        (
            [71, 105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987],
            "71 and 105",
            "raises error when two peaks in a row at beginning",
        ),
        (
            [105, 186, 266, 344, 424, 502, 586, 600, 667, 745, 825, 906, 987],
            "586 and 600",
            "raises error when two peaks in a row in middle",
        ),
        (
            [105, 186, 266, 344, 424, 502, 586, 667, 745, 825, 906, 987, 1000],
            "987 and 1000",
            "raises error when two peaks in a row at end",
        ),
    ],
)
def test_find_twitch_indices__raises_error_if_two_peaks_in_a_row__and_does_not_start_with_peak(
    new_A1, test_data, expected_match, test_description
):
    _, peak_and_valley_indices = new_A1
    _, valley_indices = peak_and_valley_indices
    peak_indices = np.asarray(test_data, dtype=np.int32)
    with pytest.raises(TwoPeaksInARowError, match=expected_match):
        find_twitch_indices((peak_indices, valley_indices))


@pytest.mark.parametrize(
    "test_data,expected_match,test_description",
    [
        (
            [70, 100, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963],
            "70 and 100",
            "raises error when two valleys in a row at beginning",
        ),
        (
            [70, 147, 220, 305, 397, 400, 463, 555, 628, 713, 779, 871, 963],
            "397 and 400",
            "raises error when two valleys in a row in middle",
        ),
        (
            [70, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963, 1000, 1001],
            "1000 and 1001",
            "raises error when two valleys in a row at end",
        ),
    ],
)
def test_find_twitch_indices__raises_error_if_two_valleys_in_a_row__and_starts_with_peak(
    new_A1, test_data, expected_match, test_description
):
    _, peak_and_valley_indices = new_A1
    peak_indices, _ = peak_and_valley_indices
    valley_indices = np.asarray(test_data, dtype=np.int32)
    with pytest.raises(TwoValleysInARowError, match=expected_match):
        find_twitch_indices((peak_indices, valley_indices))


@pytest.mark.parametrize(
    "test_data,expected_match,test_description",
    [
        (
            [0, 70, 100, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963],
            "70 and 100",
            "raises error when two valleys in a row at beginning",
        ),
        (
            [0, 70, 147, 220, 305, 397, 400, 463, 555, 628, 713, 779, 871, 963],
            "397 and 400",
            "raises error when two valleys in a row in middle",
        ),
        (
            [0, 70, 147, 220, 305, 397, 463, 555, 628, 713, 779, 871, 963, 1000, 1001],
            "1000 and 1001",
            "raises error when two valleys in a row at end",
        ),
    ],
)
def test_find_twitch_indices__raises_error_if_two_valleys_in_a_row__and_does_not_start_with_peak(
    new_A1, test_data, expected_match, test_description
):
    _, peak_and_valley_indices = new_A1
    peak_indices, _ = peak_and_valley_indices
    valley_indices = np.asarray(test_data, dtype=np.int32)
    with pytest.raises(TwoValleysInARowError, match=expected_match):
        find_twitch_indices((peak_indices, valley_indices))


def test_find_twitch_indices__returns_correct_values_with_data_that_ends_in_peak():
    peak_indices = np.array([1, 3, 5], dtype=np.int32)
    valley_indices = np.array([0, 2, 4], dtype=np.int32)
    actual = find_twitch_indices((peak_indices, valley_indices))

    assert actual[1][PRIOR_PEAK_INDEX_UUID] is None
    assert actual[3][PRIOR_PEAK_INDEX_UUID] == 1

    assert actual[1][PRIOR_VALLEY_INDEX_UUID] == 0
    assert actual[3][PRIOR_VALLEY_INDEX_UUID] == 2

    assert actual[1][SUBSEQUENT_PEAK_INDEX_UUID] == 3
    assert actual[3][SUBSEQUENT_PEAK_INDEX_UUID] == 5

    assert actual[1][SUBSEQUENT_VALLEY_INDEX_UUID] == 2
    assert actual[3][SUBSEQUENT_VALLEY_INDEX_UUID] == 4


def test_find_twitch_indices__returns_correct_values_with_data_that_ends_in_valley():
    peak_indices = np.array([1, 3, 5], dtype=np.int32)
    valley_indices = np.array([2, 4, 6], dtype=np.int32)
    actual = find_twitch_indices((peak_indices, valley_indices))

    assert actual[3][PRIOR_PEAK_INDEX_UUID] == 1
    assert actual[3][PRIOR_VALLEY_INDEX_UUID] == 2
    assert actual[3][SUBSEQUENT_PEAK_INDEX_UUID] == 5
    assert actual[3][SUBSEQUENT_VALLEY_INDEX_UUID] == 4


def test_noisy_data_A1(noisy_data_A1):
    pipeline, peak_and_valley_indices = noisy_data_A1

    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_noisy_data_A1_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices
    # TODO Tanner (11/3/20): lock this and other data in to a specific filter
    # fmt: off
    expected_peak_indices = [19, 580, 1166, 1729, 2341, 2866, 3394, 3956, 4530, 5088, 5710, 6228, 6797, 7340, 7964, 8525, 9103, 9623, 10184, 10763, 11358, 11909, 12520, 13045]
    expected_valley_indices = [330, 803, 1573, 2127, 2711, 3111, 3681, 4206, 4968, 5504, 6094, 6618, 7067, 7550, 8379, 8896, 9428, 9992, 10502, 10989, 11730, 12293, 12820]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test_noisy_data_B1(noisy_data_B1):
    pipeline, peak_and_valley_indices = noisy_data_B1
    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_noisy_data_B1_peaks.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_peak_indices = [342, 867, 1392, 1936, 2451, 3005, 3507, 4036, 4584, 5079, 5595, 6139, 6676, 7219, 7751, 8279, 8778, 9333, 9847, 10390, 10908, 11454, 11981, 12503, 13033]
    expected_valley_indices = [701, 1145, 1721, 2271, 2829, 3178, 3816, 4372, 4815, 5340, 5897, 6449, 7040, 7570, 8091, 8617, 9154, 9602, 10134, 10686, 11233, 11797, 12347, 12851]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test__B6_data_causing_TwoValleysInARowError(MA20123123__2020_10_13_173812__B6):
    pipeline, peak_and_valley_indices = MA20123123__2020_10_13_173812__B6
    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_MA20123123__2020_10_13_173812__B6.png"),
        x_bounds=(65, 75),
    )

    peak_indices, valley_indices = peak_and_valley_indices
    # find_twitch_indices(peak_and_valley_indices, filtered_data)

    # fmt: off
    expected_peak_indices = [828, 1593, 2388, 3184, 3980, 4755, 5545, 6258, 7048, 7850, 8636, 9446, 10248, 11017, 11802, 12564, 13370, 14153, 14948, 15718, 16497, 17271, 18050, 18822, 19574, 20335, 21150, 21907, 22714, 23474, 24273, 25041, 25830, 26625, 27408, 28189, 28968, 29800, 30571, 31358, 32137, 32970, 33750, 34516, 35296, 36075, 36857, 37635, 38446, 39182, 39935, 40651, 41366, 42211, 42995, 43757, 44520, 45254, 45998, 46731, 47472, 48232, 48975, 49699, 50479, 51226, 51983, 52707, 53424, 54179, 54844, 55575, 56281, 56982, 57723, 58482, 59253, 60019, 60782, 61528, 62303, 63085, 63851, 64657, 65430, 66214, 66988, 67778, 68573, 69366, 70092, 70809, 71556, 72302, 72997, 73741, 74475, 75211]
    expected_valley_indices = [559, 1338, 2054, 2873, 3752, 4555, 5282, 5994, 6812, 7413, 8182, 8989, 9852, 10642, 11434, 12258, 13055, 13942, 14728, 15498, 16188, 17024, 17669, 18504, 19381, 20119, 20864, 21556, 22510, 23279, 24008, 24859, 25636, 26430, 27222, 27975, 28765, 29567, 30254, 30942, 31910, 32482, 33476, 34099, 34991, 35836, 36576, 37270, 38185, 38830, 39733, 40406, 41179, 41823, 42619, 43533, 44256, 44906, 45785, 46373, 47259, 47852, 48738, 49504, 50292, 51053, 51712, 52500, 53220, 53723, 54485, 55337, 56083, 56649, 57501, 58312, 59058, 59771, 60585, 61183, 62017, 62877, 63646, 64315, 65212, 65912, 66790, 67592, 68370, 69182, 69870, 70570, 71222, 72108, 72793, 73488, 74236, 74983]
    # fmt: on

    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)
    assert len(valley_indices) == 98


def test__A1_data_causing_TwoValleysInARowError(MA20123123__2020_10_13_234733__A1):
    pipeline, peak_and_valley_indices = MA20123123__2020_10_13_234733__A1
    # plot and save results
    filtered_data = pipeline.get_noise_filtered_gmr()
    _plot_data(
        peak_and_valley_indices,
        filtered_data,
        os.path.join(PATH_TO_PNGS, "new_MA20123123__2020_10_13_234733__A1.png"),
    )

    peak_indices, valley_indices = peak_and_valley_indices
    find_twitch_indices(peak_and_valley_indices)

    # fmt: off
    expected_peak_indices = [625, 1314, 2030, 2718, 3426, 4123, 4840, 5533, 6227, 6934, 7633, 8301, 9009, 9739, 10517, 11275, 12035, 12799, 13577, 14326, 15105, 15872, 16645, 17416, 18175, 18954, 19706, 20478, 21250, 22005, 22792, 23592, 24361, 25169, 25961, 26748, 27528, 28324, 29119, 29921, 30711, 31510, 32330, 33146]
    expected_valley_indices = [404, 942, 1669, 2395, 3237, 3853, 4635, 5345, 6007, 6676, 7433, 8027, 8602, 9516, 10226, 11059, 11829, 12463, 13296, 14119, 14917, 15680, 16279, 17061, 17951, 18748, 19538, 20223, 21023, 21764, 22578, 23157, 24130, 24949, 25656, 26487, 27088, 28068, 28882, 29725, 30215, 31162, 32072, 32828, 33697]
    # fmt: on
    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test__D4_data_causing_TwoValleysInARowError(MA202000030__2020_12_11_233215__D4):
    _, peak_and_valley_indices = MA202000030__2020_12_11_233215__D4
    peak_indices, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_peak_indices = [257, 781, 1306, 1833, 2358, 2888, 3408, 3931, 4454, 4978, 5501, 6024, 6539, 7068, 7597]
    expected_valley_indices = [525, 997, 1487, 2177, 2716, 3237, 3750, 4289, 4759, 5239, 5717, 6372, 6895, 7334, 7895,]
    # fmt: on

    assert np.array_equal(peak_indices, expected_peak_indices)
    assert np.array_equal(valley_indices, expected_valley_indices)


def test__A3_data_causing_TwoValleysInARowError_second_peak_taller(
    MA202000127__2021_03_26_174059__A3,
):
    _, peak_and_valley_indices = MA202000127__2021_03_26_174059__A3
    _, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [637, 1361, 2174,2933,3566,4335,5107,5863,6688,7411,7933,8711,9570,10364,11176,11768,12706,13420,14050,14852,15648,16355,17189,17954,18622,19402,20151,20785,21475,22437,23061,23882,24582,25284,26023,26627,27495,28254,29039, 29794,30533,31308,32015,32570,33518,34239,34957,35696,36327,36953,37930,38685,39342,40059,40816,41426,42374,43146,43829,44515,45326,46054,46725,47521,48253,48993,49730,50421,51157,51811,52497,53279,54052,54743,55549,56250,56885,57749,58513,59191,]
    # fmt: on

    assert np.array_equal(valley_indices, expected_valley_indices)


def test__A3_data_causing_out_of_bounds_error(MA202000127__2021_04_20_212922__A3):

    _, peak_and_valley_indices = MA202000127__2021_04_20_212922__A3
    _, valley_indices = peak_and_valley_indices

    # fmt: off
    expected_valley_indices = [355, 617, 2493, 3908, 4802, 5368, 5761, 7180, 7627, 8856, 9138, 9534, 10128, 10635, 11110, 11728, 12004, 13011, 13418, 13529, 13908, 14463, 15137, 15618, 15765, 16430, 16867, 17199, 18596, 18810, 19184, 20076, 20307, 20792, 21147, 22183, 22273, 22933, 24386, 25131, 26699, 27265, 27564, 28248, 28453]
    # fmt: on
    assert np.array_equal(valley_indices, expected_valley_indices)
