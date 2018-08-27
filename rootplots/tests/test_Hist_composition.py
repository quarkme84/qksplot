from rootplots.hist import HistND
import pympler.asizeof as asizeof


def test_composition(h, bins):
    print("-"*50)
    print("Testing histogram: ", h.title)
    idx_cell = h.bins_to_cell(*bins)
    idx_bins = h.cell_to_bins(idx_cell)

    print("idx_cell:", idx_cell)
    print("idx_bins:", idx_bins)
    print("(pympler) profile has:", asizeof.asizeof(h), " bytes")


h1 = HistND(1,[0], [1], [5], title="H1")
h2 = HistND(2,[0,0], [1,1], [5,6], title="H2")
h3 = HistND(3,[0,0,0], [1,1,1], [5,6,8], title="H3")

test_composition(h1, [3])
test_composition(h2, [3,4])
test_composition(h3, [4,2,6])