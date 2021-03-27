def darken_block(self, a, b, c):
    R1, G1, B1 = self.map.get_color(a, b, c)
    R2, G2, B2 = int(float(R1) * 0.9), int(float(G1) * 0.9), int(float(B1) * 0.9)
    if R2 < 0:
        R2 = 0
    if G2 < 0:
        G2 = 0
    if B2 < 0:
        B2 = 0
    RGB = (R2, G2, B2)
    self.map.set_point(a, b, c, RGB)


def apply_script(protocol, connection, config):
    class TextureProtocol(protocol):

        def on_map_change(self, map):
            for a in range(512):
                for b in range(512):
                    for c in range(64):
                        if self.map.get_solid(a, b, c) and self.map.get_z(a, b) < 64 and self.map.is_surface(a, b, c):
                            darken_block(self, a, b, c)
            return protocol.on_map_change(self, map)

    return TextureProtocol, connection