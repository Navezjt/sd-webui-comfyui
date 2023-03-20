def preload(parser):
    parser.add_argument("--comfyui-listen", action='store_true', default=None)
    parser.add_argument("--comfyui-port", type=int, default=None)
    parser.add_argument("--comfyui-dont-upcast-attention", action='store_true', default=None)
    parser.add_argument("--comfyui-use-split-cross-attention", action='store_true', default=None)
    parser.add_argument("--comfyui-use-pytorch-cross-attention", action='store_true', default=None)
    parser.add_argument("--comfyui-disable-xformers", action='store_true', default=None)
    parser.add_argument("--comfyui-highvram", action='store_true', default=None)
    parser.add_argument("--comfyui-normalvram", action='store_true', default=None)
    parser.add_argument("--comfyui-lowvram", action='store_true', default=None)
    parser.add_argument("--comfyui-novram", action='store_true', default=None)
    parser.add_argument("--comfyui-cpu", action='store_true', default=None)
