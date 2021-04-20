from dlisio import dlis, common
import pytest
import logging
import os


# other option is to use comparision mode (benchmark-compare-fail)

# --benchmark-skip   - by default run all standard tests
# --benchmark-only   - run benchmark tests in separate CI job, mark that job as non important if it appears to false-fail often

# python -m pytest tests/dlis/test_performance.py -s --benchmark-only --benchmark-min-rounds=10 --benchmark-sort='name' --benchmark-columns='mean,min,max,stddev,rounds'

#probably can't do the same with ctests?

def analyze(benchmark, path, limit):
    if benchmark.stats.stats.mean > limit:
        pytest.fail("load of {} took longer than expected: {} ms > {} ms"
                    .format(path, benchmark.stats.stats.mean, limit))


@pytest.mark.benchmark(
    group="load-real-no-tif",
)
def test_load(benchmark):
    limit = 0.03
    path = 'data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'

    def work():
        # separate method is needed as files must be closed for every single run
        # or we run out of handles
        with dlis.load(path):
            pass

    benchmark(work)
    analyze(benchmark, path, limit)

@pytest.mark.benchmark(
    group="load-real-no-tif",
)
def test_curves(benchmark):
    limit = 0.2
    path = 'data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'

    def work():
        with dlis.load(path) as files:
            for file in files:
                for frame in file.frames:
                    _ = frame.curves()

    benchmark(work)
    analyze(benchmark, path, limit)

@pytest.mark.benchmark(
    group="load-real-no-tif",
)
def test_metadata(benchmark):
    limit = 0.2
    path = 'data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'

    def work():
        with dlis.load(path) as files:
            for file in files:
                file.load()

    benchmark(work)
    analyze(benchmark, path, limit)


def channel_tools_file(tmpdir, merge_files_manyLR):
    path = os.path.join(str(tmpdir), 'performance-tools-channels.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/origin.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',
        'data/chap4-7/eflr/tool.dlis.part',

    ]
    merge_files_manyLR(path, content)
    return path

@pytest.mark.benchmark(
    group="caching",
)
def test_no_user_caching(benchmark, tmpdir, merge_files_manyLR):
    limit = 0.3
    path = channel_tools_file(tmpdir, merge_files_manyLR)

    # real example that with caching removal cause time increase
    def work():
        with dlis.load(path) as files:
            count = 0
            for file in files:
                for channel in file.channels:
                    for tool in file.tools:
                        if channel in tool.channels:
                            count+= 1
            assert count == 84


    benchmark(work)
    analyze(benchmark, path, limit)

@pytest.mark.benchmark(
    group="caching",
)
def test_user_caching(benchmark, tmpdir, merge_files_manyLR):
    limit = 0.035
    path = channel_tools_file(tmpdir, merge_files_manyLR)

    def work():
        with dlis.load(path) as files:
            count = 0
            for file in files:
                channels = file.channels
                tools = file.tools
                tool_channels = {tool.fingerprint : tool.channels for tool in tools}
                for channel in channels:
                    for tool in tools:
                        if channel in tool_channels[tool.fingerprint]:
                            count += 1
            assert count == 84

    benchmark(work)
    analyze(benchmark, path, limit)
