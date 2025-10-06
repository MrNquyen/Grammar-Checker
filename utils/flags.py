import argparse
class Flags:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.add_core_args()

    def get_parser(self):
        return self.parser.parse_args()

    def add_core_args(self):
        # TODO: Update default values
        self.parser.add_argument_group("Core Arguments")

        self.parser.add_argument(
            "--config", type=str, default="config/config.yaml", required=False, help="config yaml file"
        )

        self.parser.add_argument(
            "--load_source_graph", action="store_true", help="Loading turboLib Knowledge Graph from existing <graph_src>.pkl"
        )

        # self.parser.add_argument(
        #     "--src_folder_path", type=str, help="TurboLib folder dir"
        # )
        self.parser.add_argument(
            "--src_engine_folder_path", type=str, help="TurboLib Engine folder dir"
        )
        self.parser.add_argument(
            "--src_custlib_folder_path", type=str, help="TurboLib Custlib folder dir"
        )

        self.parser.add_argument(
            "--graph_path_engine", type=str, help="Network X Graph Engine path"
        )

        self.parser.add_argument(
            "--graph_path_custlib", type=str, help="Network X Graph Custlib path"
        )

        self.parser.add_argument(
            "--graph_path", type=str, help="Network X Graph path"
        )
        
        self.parser.add_argument(
            "--graph_type", type=str, help="Graph type", choices=["engine", 'custlib']
        )
        