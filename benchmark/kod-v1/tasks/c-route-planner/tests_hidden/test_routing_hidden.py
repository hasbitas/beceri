import unittest

from routing import Network, reachable_within, shortest_path


class HiddenTests(unittest.TestCase):
    def test_parallel_road_never_replaces_with_longer(self):
        net = Network(directed=True)
        net.add_road("a", "b", 2)
        net.add_road("a", "b", 7)
        self.assertEqual(net.length("a", "b"), 2)
        self.assertIsNone(net.length("b", "a"))
        net.add_road("a", "b", 2)
        self.assertEqual(net.roads(), [("a", "b", 2)])

    def test_equal_cost_prefers_lexicographically_smaller_path(self):
        net = Network()
        net.add_road("s", "b", 1)
        net.add_road("b", "t", 2)
        net.add_road("s", "a", 1)
        net.add_road("a", "m", 1)
        net.add_road("m", "t", 1)
        self.assertEqual(shortest_path(net, "s", "t"), (3, ["s", "a", "m", "t"]))

    def test_zero_length_roads(self):
        net = Network()
        net.add_road("a", "b", 0)
        net.add_road("b", "c", 0)
        net.add_road("a", "c", 0)
        self.assertEqual(shortest_path(net, "a", "c"), (0, ["a", "b", "c"]))
        self.assertEqual(reachable_within(net, "a", 0), {"a": 0, "b": 0, "c": 0})

    def test_routes_never_repeat_a_place(self):
        net = Network(directed=True)
        net.add_road("s", "a", 0)
        net.add_road("a", "a", 0)
        net.add_road("a", "t", 1)
        self.assertEqual(shortest_path(net, "s", "t"), (1, ["s", "a", "t"]))
        loop = Network(directed=True)
        loop.add_road("s", "a", 0)
        loop.add_road("a", "b", 0)
        loop.add_road("b", "a", 0)
        loop.add_road("b", "t", 2)
        loop.add_road("a", "t", 2)
        self.assertEqual(shortest_path(loop, "s", "t"), (2, ["s", "a", "b", "t"]))
        self.assertEqual(shortest_path(loop, "s", "s"), (0, ["s"]))
        zero = Network()
        zero.add_road("a", "b", 0)
        zero.add_road("b", "c", 0)
        zero.add_road("c", "a", 0)
        self.assertEqual(shortest_path(zero, "a", "c"), (0, ["a", "b", "c"]))
        self.assertEqual(shortest_path(zero, "c", "a"), (0, ["c", "a"]))

    def test_budget_is_inclusive_and_ordered_by_cost_then_name(self):
        net = Network()
        net.add_road("hub", "y", 2)
        net.add_road("hub", "x", 2)
        net.add_road("hub", "w", 5)
        found = reachable_within(net, "hub", 2)
        self.assertEqual(list(found.items()), [("hub", 0), ("x", 2), ("y", 2)])
        self.assertEqual(reachable_within(net, "hub", 0), {"hub": 0})
        self.assertEqual(reachable_within(net, "hub", 4), found)

    def test_directed_roads_are_one_way(self):
        net = Network(directed=True)
        net.add_road("a", "b", 1)
        net.add_road("b", "c", 1)
        self.assertEqual(shortest_path(net, "a", "c"), (2, ["a", "b", "c"]))
        self.assertIsNone(shortest_path(net, "c", "a"))
        self.assertEqual(reachable_within(net, "c", 10), {"c": 0})

    def test_detour_beats_direct_road(self):
        net = Network()
        net.add_road("a", "d", 10)
        for left, right in (("a", "b"), ("b", "c"), ("c", "d")):
            net.add_road(left, right, 3)
        self.assertEqual(shortest_path(net, "a", "d"), (9, ["a", "b", "c", "d"]))

    def test_errors(self):
        net = Network()
        net.add_road("a", "b", 1)
        with self.assertRaises(KeyError):
            shortest_path(net, "a", "nope")
        with self.assertRaises(KeyError):
            shortest_path(net, "nope", "a")
        with self.assertRaises(KeyError):
            reachable_within(net, "nope", 3)
        with self.assertRaises(TypeError):
            reachable_within(net, "a", 1.5)
        with self.assertRaises(TypeError):
            reachable_within(net, "a", True)
        with self.assertRaises(ValueError):
            reachable_within(net, "a", -1)
        with self.assertRaises(KeyError):
            net.neighbors("nope")

    def test_road_validation_is_atomic(self):
        net = Network()
        cases = (
            (("a", "b", -1), ValueError),
            (("a", "b", 2.0), TypeError),
            (("a", "b", True), TypeError),
            (("a", "", 1), ValueError),
            (("a", 5, 1), TypeError),
            ((None, "b", 1), TypeError),
        )
        for args, error in cases:
            with self.assertRaises(error):
                net.add_road(*args)
        self.assertEqual(net.places(), [])
        with self.assertRaises(ValueError):
            net.add_place("")
        with self.assertRaises(TypeError):
            net.add_place(3)

    def test_roads_and_neighbors_listing(self):
        net = Network()
        net.add_road("b", "a", 5)
        net.add_road("b", "c", 1)
        net.add_road("c", "c", 4)
        net.add_place("lonely")
        self.assertEqual(net.roads(), [("a", "b", 5), ("b", "c", 1), ("c", "c", 4)])
        self.assertEqual(net.neighbors("b"), [("a", 5), ("c", 1)])
        self.assertEqual(net.neighbors("lonely"), [])
        self.assertEqual(net.places(), ["a", "b", "c", "lonely"])
        self.assertIsNone(net.length("a", "ghost"))


if __name__ == "__main__":
    unittest.main()
