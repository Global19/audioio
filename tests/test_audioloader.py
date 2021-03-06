from nose.tools import assert_true
import numpy as np
import audioio.audiowriter as aw
import audioio.audioloader as al

def test_audioloader():
    # generate data:
    samplerate = 44100.0
    duration = 100.0
    channels = 2
    t = np.arange(int(duration*samplerate))/samplerate
    data = np.sin(2.0*np.pi*880.0*t) * t/duration
    data = data.reshape((-1, 1))
    for k in range(data.shape[1], channels):
        data = np.hstack((data, data[:,0].reshape((-1, 1))/k))

    # parameter for wav file:
    filename = 'test.wav'
    format = 'wav'
    encoding = 'PCM_16'
    tolerance = 2.0**(-15)

    # write:
    aw.write_wave(filename, data, samplerate, encoding=encoding)

    audio_funcs = [
        ['soundfile', al.load_soundfile],
        ['scikits.audiolab', al.load_audiolab],
        ['wavefile', al.load_wavefile],
        ['audioread', al.load_audioread],
        ['wave', al.load_wave],
        ['ewave', al.load_ewave],
        ]

    for lib, read_func in audio_funcs:
        if not al.audio_modules[lib]:
            continue
        print('%s module:' % lib)
        # load full data:
        full_data, rate = read_func(filename)

        # load on demand:
        data = al.AudioLoader()
        load_funcs = {
            'soundfile': data.open_soundfile,
            'scikits.audiolab': data.open_audiolab,
            'wavefile': data.open_wavefile,
            'audioread': data.open_audioread,
            'wave': data.open_wave,
            'ewave': data.open_ewave,
            }
        load_funcs[lib](filename, 10.0, 2.0)

        nframes = int(1.5*data.samplerate)
        # check access:
        ntests = 1000
        step = int(len(data)/ntests)
        success = -1
        print('  check random single frame access...')
        for inx in np.random.randint(0, len(data), ntests):
            if np.any(np.abs(full_data[inx] - data[inx]) > tolerance):
                success = inx
                break
        assert_true(success < 0, 'single random frame access failed at index %d with %s module' % (success, lib))
        print('  check random frame slice access...')
        for inx in np.random.randint(0, len(data)-nframes, ntests):
            if np.any(np.abs(full_data[inx:inx+nframes] - data[inx:inx+nframes]) > tolerance):
                success = inx
                break
        assert_true(success < 0, 'random frame slice access failed at index %d with %s module' % (success, lib))
        print('  check forward slice access...')
        for inx in range(0, len(data)-nframes, step):
            if np.any(np.abs(full_data[inx:inx+nframes] - data[inx:inx+nframes]) > tolerance):
                success = inx
                break
        assert_true(success < 0, 'frame slice access forward failed at index %d with %s module' % (success, lib))
        print('  check backward slice access...')
        for inx in range(len(data)-nframes, 0, -step):
            if np.any(np.abs(full_data[inx:inx+nframes] - data[inx:inx+nframes]) > tolerance):
                success = inx
                break
        assert_true(success < 0, 'frame slice access backward failed at index %d with %s module' % (success, lib))

        data.close()

    
