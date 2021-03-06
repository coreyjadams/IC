import numpy as np

from pytest        import mark
from pytest        import raises

from hypothesis             import given
from hypothesis.strategies  import floats
from hypothesis.strategies  import integers
from hypothesis.strategies  import composite
from hypothesis.extra.numpy import arrays

from .. core.core_functions import weighted_mean_and_std
from .. core.exceptions     import InconsistentS12dIpmtd
from .. core.exceptions     import InitializedEmptyPmapObject

from .. reco.pmaps_functions_c import integrate_sipm_charges_in_peak
from .. reco  import pmaps_functions as pmapf
from .  pmaps import S1
from .  pmaps import S2
from .  pmaps import S12
from .  pmaps import S2Si
from .  pmaps import S12Pmt
from .  pmaps import S1Pmt
from .  pmaps import S2Pmt
from .  pmaps import Peak
from .  pmaps import check_s2d_and_s2sid_share_peaks
from .. core.core_functions    import loc_elem_1d


@composite
def peak_input(draw, min_size=1, max_size=100):
    size = draw(integers(min_size, max_size))
    t    = draw(arrays(float, size, floats(0.1, 10000.), unique=True)); t.sort() # times in order!
    E    = draw(arrays(float, size, floats(-10., 1000.)))
    return size, t, E


@composite
def s2si_input(draw, min_size=1, max_size=10):
    size = draw(integers(min_size, max_size))
    t    = draw(arrays(np.double, size, floats(1, 10000))); t.sort() # times in order!
    E    = draw(arrays(np.double, size, integers(10, 1000)))
    qs1  = draw(arrays(np.double, size, integers(5, 50)))
    qs2  = draw(arrays(np.double, size, integers(5200, 60000)))
    return size, t, E, qs1, qs2


def rms(x, y):
    if len(x) == len(y) < 2: return 0
    return weighted_mean_and_std(x, y)[1]


@given(peak_input())
def test_peak(peak_pars):
    size, t, E = peak_pars
    wf =  Peak(t, E)
    if (np.any(np.isnan(t))  or
       np.any(np.isnan(E))):
       assert  wf.good_waveform == False
    else:
       assert  wf.good_waveform == True

    positive = wf.E > 0

    np.allclose (wf.t , t, rtol=1e-4)
    np.allclose (wf.E , E, rtol=1e-4)
    np.isclose (wf.total_energy , np.sum(E), rtol=1e-4)
    np.isclose (wf.height , np.max(E), rtol=1e-4)
    np.isclose (wf.tpeak , t[np.argmax(E)], rtol=1e-4)
    np.isclose (wf.width , t[-1] - t[0], rtol=1e-4)
    np.isclose (wf.tmin_tmax.min , t[0], rtol=1e-4)
    np.isclose (wf.tmin_tmax.max , t[-1], rtol=1e-4)
    np.isclose (wf.rms, rms(wf.t[positive], wf.E[positive]), rtol=1e-4)
    assert wf.number_of_samples == len(t)


@given(peak_input())
def test_peak_above_thr(peak_pars):
    size, t, E = peak_pars
    ethr       = 10
    tth        = t[E > ethr]
    eth        = E[E > ethr]
    w_thr      = -1
    esum_thr   = -1
    height_thr = -1
    rms_thr    = -1
    if len(eth):
        t0 = (loc_elem_1d(E, eth[0]))
        t1 = (loc_elem_1d(E, eth[-1]))

        w_thr      = t[t1] - t[t0]
        esum_thr   = np.sum(eth)
        height_thr = np.max(eth)
        rms_thr    = rms(tth, eth)

    wf =  Peak(t, E)
    if (np.any(np.isnan(t))  or
       np.any(np.isnan(E))):
       assert  wf.good_waveform == False
    else:
       assert  wf.good_waveform == True

    np.isclose (wf.total_energy_above_threshold(ethr),   esum_thr, rtol=1e-4)
    np.isclose (wf.      height_above_threshold(ethr), height_thr, rtol=1e-4)
    np.isclose (wf.       width_above_threshold(ethr),      w_thr, rtol=1e-4)
    np.isclose (wf.         rms_above_threshold(ethr),    rms_thr, rtol=1e-4)


@given(peak_input())
def test_s1__(wform):
    _, t1, E1 = wform
    _, t2, E2 = wform

    s1d = {0: [t1, E1], 1: [t2, E2] }
    s1 = S1(s1d)

    assert s1.number_of_peaks == len(s1d)
    for i in s1.peak_collection():
        if s1.peak_waveform(i).good_waveform:
            np.allclose (s1.peak_waveform(i).t , s1d[i][0], rtol=1e-4)
            np.allclose (s1.peak_waveform(i).E , s1d[i][1], rtol=1e-4)


def test_s1_s2(KrMC_pmaps):
    *_, pmaps = KrMC_pmaps
    for attr in ("s1", "s2"):
        s12_evts  = getattr(pmaps, attr)
        peak_attr = attr + "d"
        for evt_no, s12 in s12_evts.items():
            assert s12.number_of_peaks == len(s12.peaks)

            peak_dict = getattr(s12, peak_attr)
            for peak_no, (t, E) in peak_dict.items():
                pwf = s12.peak_waveform(peak_no)
                pk =  Peak(t, E)
                np.allclose(pwf.t , pk.t, rtol=1e-4)
                np.allclose(pwf.E , pk.E, rtol=1e-4)


def test_s2si(KrMC_pmaps):
    *_, pmaps = KrMC_pmaps
    s2si_dict = pmaps.s2si

    for evt_no, s2si in s2si_dict.items():
        Q_dict = s2si.peak_and_sipm_total_energy_dict()

        for peak_number in s2si.peak_collection():
            assert (s2si.number_of_sipms_in_peak(peak_number) ==
                    len(s2si.s2sid[peak_number]))

            np.array_equal(np.array(s2si.sipms_in_peak(peak_number)),
                           np.array(s2si.s2sid[peak_number].keys()))

            Q_sipm_dict = s2si.sipm_total_energy_dict(peak_number)
            qdict = Q_dict[peak_number]

            for sipm_number in s2si.sipms_in_peak(peak_number):
                Q = np.sum(s2si.s2sid[peak_number][sipm_number])
                np.allclose(Q_sipm_dict[sipm_number] , Q)
                np.allclose(qdict[sipm_number] , Q)
                w   = s2si.sipm_waveform(peak_number, sipm_number)
                wzs = s2si.sipm_waveform_zs(peak_number, sipm_number)
                E   = s2si.s2sid[peak_number][sipm_number]
                t = s2si.peak_waveform(peak_number).t
                np.allclose(w.E , E)
                np.allclose(wzs.E , E[E>0])
                np.allclose(wzs.t , t[E>0])


@given(s2si_input())
def test_integrate_sipm_charges_in_peak_as_dict(s2si_pars):
    size, t, E, qs1, qs2 = s2si_pars
    sipm1 = 1000
    sipm2 = 1001

    sipms = {sipm1: qs1, sipm2: qs2}
    peak_number = 0
    s2sid = {peak_number:sipms}
    s2d = {peak_number:[t, E]}
    s2si = S2Si(s2d,s2sid)
    Qs    = {sipm1: np.sum(qs1),
            sipm2: np.sum(qs2)}
    assert pmapf._integrate_sipm_charges_in_peak_as_dict(sipms) == Qs
    assert s2si.sipm_total_energy_dict(peak_number) == Qs


@given(s2si_input())
def test_integrate_sipm_charges_in_peak(s2si_pars):
    size, t, E, qs1, qs2 = s2si_pars
    sipm1 = 1000
    sipm2 = 1001
    sipms = {sipm1: qs1, sipm2: qs2}
    peak_number = 0
    s2sid = {peak_number:sipms}
    s2d = {peak_number:[t, E]}
    s2si = S2Si(s2d,s2sid)

    ids, Qs =  pmapf._integrate_sipm_charges_in_peak(sipms)
    assert np.array_equal(ids, np.array((  sipm1,    sipm2)))
    assert np.array_equal(Qs , np.array((sum(qs1), sum(qs2))))

    ids_c, Qs_c =  integrate_sipm_charges_in_peak(s2si, peak_number)
    assert np.array_equal(ids, ids_c)
    assert np.array_equal(Qs , Qs_c)


def test_integrate_S2Si_charge():
    peak1 = 0
    sipm1_1, Q1_1 = 1000, list(range(5))
    sipm1_2, Q1_2 = 1001, list(range(10))

    peak2 = 1
    sipm2_1, Q2_1 =  999, [6,4,9,7]
    sipm2_2, Q2_2 =  456, [8,4,3,5]
    sipm2_3, Q2_3 = 1234, [6,2,0,0]
    sipm2_4, Q2_4 =  666, [0,0,0,0] # !!! Zero charge

    t1 = np.array([1,2,3,4], dtype=np.double)
    E1 = np.array([10,20,30,40], dtype=np.double)

    t2 = np.array([5,6,7,8], dtype=np.double)
    E2 = np.array([50,60,70,80], dtype=np.double)

    s2sid = {peak1 : {sipm1_1 : Q1_1,
                     sipm1_2 : Q1_2},
            peak2 : {sipm2_1 : Q2_1,
                     sipm2_2 : Q2_2,
                     sipm2_3 : Q2_3,
                     sipm2_4 : Q2_4}}
    s2d   = {peak1 : [t1,E1],
            peak2 : [t2,E2]}

    s2si = S2Si(s2d,s2sid)

    integrated_S2Si = pmapf._integrate_S2Si_charge(s2sid)
    assert integrated_S2Si == {peak1 : {sipm1_1 : sum(Q1_1),
                                        sipm1_2 : sum(Q1_2)},
                               peak2 : {sipm2_1 : sum(Q2_1),
                                        sipm2_2 : sum(Q2_2),
                                        sipm2_3 : sum(Q2_3),
                                        sipm2_4 : sum(Q2_4)}}
    assert s2si.peak_and_sipm_total_energy_dict() == integrated_S2Si


def test_check_s2d_and_s2sid_share_peaks():
    s2d   = {}
    s2sid = {}
    for pn in range(100):
        s2d[pn] = -1*pn
        if pn % 2 == 0:
            s2sid[pn] = s2d[pn]
    s2d_shared_peaks = check_s2d_and_s2sid_share_peaks(s2d, s2sid)

    for pn in s2d_shared_peaks:
        assert pn in s2sid
        assert pn % 2 == 0


def test_S12Pmt_raises_error_when_s2_peak_E_not_equal_to_sum_of_s12pmt_peak():
    timebins = 10
    npmts  = 12
    ipmtd = {0: np.random.random((npmts, timebins))}
    s12d    = {0: np.array([list(range(timebins)), ipmtd[0].sum(axis=0)])}
    ipmtd[0][-1, -1] += .1
    with raises(InconsistentS12dIpmtd):
        S12Pmt(s12d, ipmtd)


def test_S12Pmt_pmt_waveform():
    timebins = 10
    npmts = 5
    # construct dicts
    for peak in range(3):
        ipmtd = {peak: np.random.random((npmts, timebins))}
        s12d    = {peak: np.array([list(range(timebins)), ipmtd[peak].sum(axis=0)])}
    # get pmt s12pmt
    s12pmt = S12Pmt(s12d, ipmtd)
    for pn in s12pmt.peaks:
        for pmt in range(npmts):
            assert (s12pmt.pmt_waveform(pn, pmt).t == s12d   [pn][  0]).all()
            assert (s12pmt.pmt_waveform(pn, pmt).E == ipmtd[pn][pmt]).all()


def test_S12Pmt_pmt_total_energy_in_peak():
    timebins = 10
    npmts  = 12
    ipmtd = {0: np.random.random((npmts, timebins))}
    s12d    = {0: np.array([list(range(timebins)), ipmtd[0].sum(axis=0)])}
    s12pmt  = S12Pmt(s12d, ipmtd)
    for pmt in range(npmts):
        assert s12pmt.pmt_total_energy_in_peak(0, pmt) == ipmtd[0][pmt].sum()


def test_pmt_total_energy():
    timebins = 10
    npmts = 5
    # construct dicts
    for peak in range(3):
        ipmtd = {peak: np.random.random((npmts, timebins))}
        s12d    = {peak: np.array([list(range(timebins)), ipmtd[peak].sum(axis=0)])}
    # get pmt s12pmt
    s12pmt = S12Pmt(s12d, ipmtd)
    for pmt in range(npmts):
        s = 0
        for pn in s12pmt.peaks: s += s12pmt.pmt_total_energy_in_peak(pn, pmt)
        assert s12pmt.pmt_total_energy(pmt) == s


@mark.parametrize("constructor, args",
    ((Peak  , (np.array([],dtype=np.float64), np.array([], np.float64))),
     (S1    , ({},   )),
     (S2    , ({},   )),
     (S12   , ({},   )),
     (S2Si  , ({}, {})),
     (S1Pmt , ({}, {})),
     (S2Pmt , ({}, {})),
     (S12Pmt, ({}, {}))))
def test_pmap_constructors_raise_exception_when_initialized_with_empty_dicts(constructor, args):
    with raises(InitializedEmptyPmapObject):
        constructor(*args)
