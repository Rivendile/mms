"""A pipeline executable."""
from alpa_serve.profiling import ParallelConfig, ProfilingResult
from alpa_serve.simulator.cluster import VirtualMesh
from alpa_serve.simulator.event_loop import wait_multi_stream


class Executable:
    def __init__(self,
                 profiling_result: ProfilingResult,
                 parallel_config: ParallelConfig,
                 virtual_mesh: VirtualMesh):
        self.profile = profiling_result
        self.parallel_config = parallel_config
        self.stage_latency = profiling_result.stage_latency[parallel_config]

        # launch or connect to a mesh group
        submesh_shapes = (
            (parallel_config.dp, parallel_config.op),) * parallel_config.pp
        if virtual_mesh.launched_mesh_group:
            assert submesh_shape == virtual_mesh.submesh_shapes
            mesh_group = virtual_mesh.launched_mesh_group
        else:
            mesh_group = virtual_mesh.launch_mesh_group(submesh_shapes)

        self.mesh_group = mesh_group

    async def handle_request(self, request):
        batch_size = 1

        latencies = self.stage_latency[batch_size]
        for mesh, latency in zip(self.mesh_group.meshes, latencies):

            streams = [g.stream_name for g in mesh.gpus]
            durations = [latency] * len(streams)
            await wait_multi_stream(streams, durations)
