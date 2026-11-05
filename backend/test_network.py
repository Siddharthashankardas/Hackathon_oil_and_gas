from app.services.network_builder import build_initial_network

network = build_initial_network()

print("Network:", network.network_version)
print("Number of nodes:", len(network.nodes))
print("Number of pipe segments:", len(network.segments))

for segment in network.segments:
    print(
        segment.segment_id,
        segment.from_node,
        "->",
        segment.to_node
    )