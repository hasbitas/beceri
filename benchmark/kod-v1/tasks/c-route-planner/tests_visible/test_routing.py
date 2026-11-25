import unittest

from routing import Network, reachable_within, shortest_path


def grid_network():
    net = Network()
    net.add_road("A", "B", 4)
    net.add_road("A", "C", 1)
    net.add_road("C", "B", 2)
    net.add_road("B", "D", 5)
    net.add_place("Z")
    return net


class VisibleTests(unittest.TestCase):
    def test_shortest_path_and_cost(self):
        net = grid_network()
        self.assertEqual(shortest_path(net, "A", "D"), (8, ["A", "C", "B", "D"]))
        self.assertEqual(shortest_path(net, "D", "A"), (8, ["D", "B", "C", "A"]))

    def test_unreachable_and_same_place(self):
        net = grid_network()
        self.assertIsNone(shortest_path(net, "A", "Z"))
        self.assertEqual(shortest_path(net, "Z", "Z"), (0, ["Z"]))

    def test_reachable_within_budget(self):
        net = grid_network()
        self.assertEqual(reachable_within(net, "A", 3), {"A": 0, "C": 1, "B": 3})
        self.assertEqual(list(reachable_within(net, "A", 9)), ["A", "C", "B", "D"])

    def test_parallel_roads_keep_the_shorter(self):
        net = Network()
        net.add_road("P", "Q", 9)
        net.add_road("P", "Q", 3)
        self.assertEqual(net.length("P", "Q"), 3)
        self.assertEqual(net.length("Q", "P"), 3)


if __name__ == "__main__":
    unittest.main()
