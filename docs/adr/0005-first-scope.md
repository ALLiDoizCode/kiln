# 5. First scope: static, stylised low-poly props

The pipeline is being proven on static hard-surface props in a flat-colour, low-poly style. That removes UV quality, baking and texture authoring from the first iterations, which are the stages hardest to check automatically, and avoids characters, where the checks cannot stand in for an artist.

Physics will use Avian, with collision shapes as separately named meshes so the convention can be checked by a script. Neither is implemented yet; the naming rule gets its own ADR when the first collider is built.
