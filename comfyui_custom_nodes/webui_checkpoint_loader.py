import webui_process
from comfy.sd import load_checkpoint_guess_config
from comfy import utils


class CheckpointLoaderPatched:
    def __init__(self, state_dict):
        self.state_dict = state_dict

    def __enter__(self):
        self.original_loader = utils.load_torch_file
        utils.load_torch_file = CheckpointLoaderPatched.load_torch_file_patch
        return self

    def __exit__(self, type, value, traceback):
        utils.load_torch_file = self.original_loader

    @staticmethod
    def load_torch_file_patch(state_dict, safe_load=False):
        return state_dict.copy()

    def load(self):
        return load_checkpoint_guess_config(self.state_dict)


class WebuiCheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                    "void": ("VOID", ),
            },
        }
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    CATEGORY = "loaders"

    def load_checkpoint(self, void):
        state_dict = webui_process.fetch_model_state_dict()
        with CheckpointLoaderPatched(state_dict) as patched_loader:
            return patched_loader.load()


NODE_CLASS_MAPPINGS = {
    "WebuiCheckpointLoader": WebuiCheckpointLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WebuiCheckpointLoader": 'Load Webui Checkpoint',
}
