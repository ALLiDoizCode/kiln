# Style reference board (candidate)

Research date: 2026-10-04. Audience: the owner, who has no 3D art background and will use this board to judge the look test (github.com/ALLiDoizCode/pit issue #1) and every later asset review by eye.

Vocabulary follows `CONTEXT.md` (**pit**, **layer**, **descent**, **ascent**, **curse**) and the style line in `docs/adr/0007-game-target-and-metrics.md`: flat-colour low-poly with bevels, a strict palette per layer, atmosphere from lighting and fog in the engine.

**How to read this document**

- Every image was downloaded and looked at on 2026-10-04. Descriptions say what is in the picture, not what the game is known for.
- Images are other people's copyrighted work. This file only **links** to them. Local copies are in `docs/style/refs/` (git-ignored, never commit them); the local filename is given beside each link.
- Facts about a game (developer, publisher, genre, features) come from its Steam store page data, fetched the same day. Facts about the *Made in Abyss* backgrounds come from the gallery of Inspired Inc., the studio that painted them.
- **[observation]** means it is what I see in the image, not something the developer states. Names of rendering techniques are observations unless a source is linked.
- **unverified** means I could not confirm it from a first-party source. All such items are collected in [section 8](#8-unverified-items).
- Hex colours and contrast numbers were measured with ImageMagick on the downloaded files and are **approximate**: they depend on the crop, the JPEG compression and the one frame chosen.

**Art terms used, defined once**

- **Low-poly**: models built from few, visibly flat faces.
- **Flat shading**: each face is one uniform tone, so the edges between faces show as sharp lines. The opposite is **smooth shading**, where tone blends across faces and the surface looks rounded.
- **Flat colour**: a surface gets one plain colour, with no painted or photographic detail (a **texture**) on it.
- **Bevel**: a small angled face cut along an edge so the edge catches a line of light instead of being razor sharp.
- **Value**: how light or dark a colour is, ignoring its hue. **Saturation**: how vivid it is (grey is zero saturation).
- **Silhouette**: the outline of a shape seen as a solid blob.
- **Fog / haze / atmospheric perspective**: things further away get paler (or darker), lose contrast and drift toward one fog colour. This is the main way a picture shows distance.
- **Contrast**: the spread between the lightest and darkest tones in an area. Below it is reported as the standard deviation of brightness on a 0 to 1 scale; bigger means more contrast.
- **Light shaft**: a visible beam of light through haze.
- **Key art**: a marketing illustration, not a frame of the game.
- **HUD**: on-screen interface (health bars, ammo counts).

---

## 1. The board at a glance

| # | Pick | Reference for | Local file |
|---|------|---------------|------------|
| 1 | *Made in Abyss*: the pit seen from above | scale, palette | `01-mia-pit-from-above.jpg` |
| 2 | *Made in Abyss*: ledges and waterfall in mist | atmosphere in a vertical space, beauty | `02-mia-ledges-waterfall-mist.jpg` |
| 3 | *Made in Abyss*: orange ground under teal overhangs | palette, layer identity | `03-mia-deep-layer-orange-teal.jpg` |
| 4 | Deep Rock Galactic: sandstone cave | atmosphere and scale with flat-shaded terrain, first-person | `04-drg-sandstone-cave.jpg` |
| 5 | Jusant: climber on a red wall above clouds | scale, climbing, palette | `05-jusant-climber-red-wall.jpg` |
| 6 | Lonely Mountains: Downhill: misty forest | beauty in exactly the chosen style, fog | `06-lmd-misty-forest.jpg` |
| 7 | Deep Rock Galactic: crate and tools close up | close-up readability | `07-drg-crate-closeup.jpg` |
| 8 | Ylands: cabin, log pile, anvil in snow | building, props | `08-ylands-cabin-snow.jpg` |

Picks 1 to 3 are paintings and set the **target mood**. Picks 4 to 8 are shipped games and show **what the chosen style can actually reach**. A look test that matches 4 to 8 in craft and 1 to 3 in mood has passed.

---

## 2. Primary picks

### 1. *Made in Abyss*: the pit seen from above

- Image: <https://www.inspired.jp/wp/wp-content/uploads/12-3.jpg> (local `01-mia-pit-from-above.jpg`, 870x485)
- Source page: Inspired Inc. official gallery, entry "メイドインアビス012", <https://www.inspired.jp/gallery/page/7/>
- Owner: copyright line printed in the image reads "© 2017 つくしあきひと・竹書房／メイドインアビス製作委員会" (Akihito Tsukushi, Takeshobo, the Made in Abyss production committee). Painted by Inspired Inc.
- Reference for: **scale**, **palette**.
- What is in it: an aerial view of a huge circular hole in an island at sunset. The rim is lit warm orange; the hole is dark blue-grey with a ring of cloud inside it. Thin vertical white lines (waterfalls) run down the inner wall. No characters, no logo.

Properties worth matching:
1. **Warm rim, cool depth.** Everything lit by the sun is orange to tan; everything inside the pit is blue-grey to near-black. The two halves of the palette do not mix.
2. **Clouds inside the pit, below the viewer.** Seeing weather beneath you is what says "this is deep". A view down from the rim should show a fog or cloud deck part-way down, not a clear view to a floor.
3. **The far side of the pit is visible but pale.** The opposite rim is lighter and lower in contrast than the near rim, so the eye reads the width.
4. **Tiny repeated marks give size.** The white waterfall lines and the speckle of buildings are one or two pixels wide; nothing in the frame is large except the pit.

Do not take: the ring-shaped town on the rim, the island setting, or the painted rock detail (this is a hand-painted image; our surfaces are flat colour).

Approximate palette (8 colours, most common first): `#3D3B43` `#5E4F55` `#CBB3B6` `#9D6A54` `#D39560` `#566B9A` `#B1724B` `#718AB5`

### 2. *Made in Abyss*: ledges and waterfall in mist

- Image: <https://www.inspired.jp/wp/wp-content/uploads/01-2.jpg> (local `02-mia-ledges-waterfall-mist.jpg`, 870x632)
- Source page: Inspired Inc. official gallery, entry "メイドインアビス001", <https://www.inspired.jp/gallery/page/6/>
- Owner: same copyright line as pick 1. Painted by Inspired Inc.
- Reference for: **atmosphere in a deep vertical space**, **beauty**.
- What is in it: grassy ledges jut out from a cliff on the right, stacked one above another. A tall waterfall drops through the middle into cloud. The far wall on the left is almost dissolved in blue-grey haze. Diagonal light shafts cross the frame. No characters, no logo.

Properties worth matching:
1. **Three distance bands, each paler and flatter than the one in front.** Measured brightness (0 to 1) rises from about 0.38 on the near ledge, to 0.44 on the middle ledge, to 0.55 on the far wall. Contrast falls from about 0.14 to 0.12 to 0.04: the far wall has under a third of the near ledge's contrast.
2. **Far things turn into the fog colour.** The far wall is the same pale blue-grey (`#91A1AD` to `#B6C7D5`) as the mist. Only its outline remains.
3. **One saturated colour, kept for the near ground.** The green is used only on the nearest ledges; everything else is grey-blue.
4. **Overhangs.** Ledges stick out past the rock under them and their undersides are in shadow. This is what makes a wall read as climbable and layered, and it is cheap to build.
5. **Visible light shafts** crossing in front of the far wall, so the air itself has a shape.

Do not take: painted leaf and grass detail, or the specific flora. Match the banding and the fog, not the brushwork.

Approximate palette (7 colours, most common first): `#B6C7D5` `#748A9D` `#91A1AD` `#55676C` `#314D48` `#667886` `#6B8E6B`

### 3. *Made in Abyss*: orange ground under teal overhangs

- Image: <https://www.inspired.jp/wp/wp-content/uploads/05.jpg> (local `03-mia-deep-layer-orange-teal.jpg`, 870x489)
- Source page: Inspired Inc. official gallery, entry "劇場版「メイドインアビス」-深き魂の黎明-005" (the film *Dawn of the Deep Soul*), <https://www.inspired.jp/gallery/page/14/>
- Owner: the film's production committee (the copyright line in the image is small; the gallery title names the film). Painted by Inspired Inc.
- Reference for: **palette**, **layer identity** (how one layer can look like nowhere else).
- What is in it: a rolling field of orange-red flowers in the foreground. Behind it a clump of tall olive-yellow twisted growths. Behind and above that, huge dark shapes hang from the ceiling with thin waterfalls falling from them, all in dark teal. No sky.

Properties worth matching:
1. **Two-colour scheme.** Orange ground, teal everything else, with olive as the only bridge. A layer palette of this kind can be written down in five or six colours and enforced.
2. **Distance goes darker, not lighter.** Unlike pick 2, the far shapes sink toward dark teal (brightness about 0.25 against 0.35 for the ground). Deep layers have no sky, so fog there should be dark.
3. **Far contrast collapses.** Contrast is about 0.085 on the ground and about 0.022 in the far overhangs: a quarter. The overhangs are pure silhouettes.
4. **A ceiling.** Things hang down from above. In a pit, "up" should be closed in by the layer above, and that is part of the mood.
5. **Saturation is rationed.** The single brightest colour (`#EA8055`) covers only a few per cent of the frame.

Do not take: the flower field and the twisted growths are named, recognisable designs from the source. Take the colour logic only.

Approximate palette (8 colours, most common first): `#5D4B2F` `#334654` `#293031` `#4A3C24` `#293A48` `#A85B38` `#535059` `#EA8055`

### 4. Deep Rock Galactic: sandstone cave

- Image: <https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/548430/913b717769f73ef0a72fc67599f1e26ed5ae35a2/ss_913b717769f73ef0a72fc67599f1e26ed5ae35a2.1920x1080.jpg> (local `04-drg-sandstone-cave.jpg`)
- Source page: Steam store page, <https://store.steampowered.com/app/548430/Deep_Rock_Galactic/>
- Owner: Ghost Ship Games (developer), Coffee Stain Publishing (publisher).
- Reference for: **atmosphere** and **scale** with flat-shaded terrain, at eye level.
- What is in it: a wide cave with an orange floor, two stacked-rock pillars, a giant rib cage on the right and scattered yellow rocks. One small glowing lamp sits on the floor. Far back between the pillars a tiny figure stands on a ledge with a headlamp beam. Beyond that the cave falls off into black. No HUD, no weapon in frame.

Why it matters: the store page describes the game as a "co-op FPS" with "procedurally-generated destructible environments" and "11 distinct biomes". That is the nearest shipped match to a first-person game on procedural terrain with a different look per region.

Properties worth matching:
1. **Every surface is a plain colour broken into flat faces** [observation]. There is no rock texture, and the cave still reads as rock because the faces catch light at different angles.
2. **Light makes the picture, and most of the frame is dark.** The most common colour is near-black `#1F0D04`. Light comes from small local sources (the lamp, the headlamp), each with a visible pool.
3. **One hue family per biome.** Floor, pillars, rocks and bones are all orange, amber or cream. Accents are tiny.
4. **Distance fades to darkness.** Brightness drops from about 0.42 on the near floor to about 0.19 in the far cave, and saturation drops from nearly full to under half.
5. **A tiny lit figure gives the size of the cave.** Without the figure between the pillars the pillars could be any height.

Do not take: the combat, the noise of effects in the other store screenshots, or full-saturation colour everywhere (see tension 2). Several other screenshots on the page are HUD-heavy or menu screens and were rejected.

Approximate palette (8 colours, most common first): `#1F0D04` `#5B2A07` `#9F5707` `#724A10` `#EA9909` `#B05601` `#D5AC2D` `#FFFFC0`

### 5. Jusant: climber on a red wall above clouds

- Image: <https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1977170/ss_46d56466bf68624124cdf6ec80531f99d6ce7a94.1920x1080.jpg> (local `05-jusant-climber-red-wall.jpg`, served at 1717x966)
- Source page: Steam store page, <https://store.steampowered.com/app/1977170/Jusant/>
- Owner: DON'T NOD (developer and publisher).
- Reference for: **scale** (a small figure against a vast drop), **climbing**, **palette**.
- What is in it: a climber hangs from a rope on a red-orange rock wall that fills the left two thirds of the frame. To the right the wall continues downward with wooden platforms and ladders built onto it, getting smaller. Far below is a flat sea of pale cloud under a grey-blue sky. Two small interface marks sit beside the climber (a stamina arc and a grab icon).

Why it matters: the store page calls it a "climbing game" in which you "scale an immeasurably tall tower" through "diverse biomes". It is third-person, not first-person.

Properties worth matching:
1. **The wall is one colour with soft tone changes** [observation]. Rock is red with slightly lighter and darker patches and no fine detail. Handholds are small dark pockets that read at a glance.
2. **Built things shrink down the wall.** Platforms and ladders repeat at smaller and smaller sizes; the eye counts them and gets the height.
3. **The drop ends in cloud, not ground.** As in pick 1, you never see the bottom.
4. **Near is vivid, far is grey.** Saturation is about 0.60 on the near wall and about 0.07 in the far clouds.
5. **Two blocks of colour.** Red wall and grey-white distance account for nearly the whole frame.

Do not take: the smooth, rounded, sculpted rock. Jusant's surfaces are smooth-shaded with soft gradients [observation], which is not the flat-shaded, bevelled look chosen in ADR 0007 (see tension 1). Do not take the third-person framing either.

Approximate palette (8 colours, most common first): `#9D2F27` `#62252C` `#A1A0A4` `#AB4A34` `#B56047` `#523443` `#C2C0BE` `#9A8E88`

### 6. Lonely Mountains: Downhill: misty forest

- Image: <https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/711540/ss_6070525d1a46b4b7ca6dc22ba8fd5ca2d19058b1.1920x1080.jpg> (local `06-lmd-misty-forest.jpg`)
- Source page: Steam store page, <https://store.steampowered.com/app/711540/Lonely_Mountains_Downhill/>
- Owner: Megagon Industries (developer and publisher).
- Reference for: **beauty** in exactly the chosen style; **fog**.
- What is in it: a small cyclist in red crosses a fallen mossy log over a stream. Slopes, rocks and tree trunks are large flat-faced green and grey shapes. Small white flowers and a few plants sit on the near slope. Everything beyond the middle distance dissolves into pale blue-green mist.

Why it matters: of all the games looked at, this is the closest to "flat-colour low-poly, atmosphere from lighting and fog" [observation]. If the owner finds this image beautiful, the style in ADR 0007 can be beautiful.

Properties worth matching:
1. **Large flat faces, few colours per object.** A rock is two or three greys. A slope is two greens. No texture is needed to tell rock from moss from wood.
2. **Soft shadows on hard shapes.** The faces are sharp-edged but the shadows cast across them are soft and tinted blue-green, not black.
3. **Fog does the depth.** Brightness goes from about 0.35 near, to 0.55 in the middle, to 0.68 far; contrast falls from about 0.07 to 0.03. The far trees are flat pale shapes.
4. **Small detail is spent only near the camera.** Flowers, grass tufts and ferns appear only in the foreground; the distance is bare shapes.
5. **One accent colour.** The red rider is the only warm colour in the frame, so the eye finds the figure at once.

Do not take: the camera. It is high and far away, so nothing here proves the style holds at 0.5 m. The depth-of-field blur (out-of-focus foreground and background) is a camera effect that does not fit a first-person game.

Approximate palette (7 colours, most common first): `#739290` `#4F6A67` `#8EA9AA` `#355347` `#688D71` `#617A84` `#A3BEC3`

### 7. Deep Rock Galactic: crate and tools close up

- Image: <https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/548430/5be477305106e6849cd4dab968fa38f87f5cb46c/ss_5be477305106e6849cd4dab968fa38f87f5cb46c.1920x1080.jpg> (local `07-drg-crate-closeup.jpg`)
- Source page: Steam store page, <https://store.steampowered.com/app/548430/Deep_Rock_Galactic/>
- Owner: Ghost Ship Games, Coffee Stain Publishing.
- Reference for: **close-up readability**. This is the nearest thing found to the pipeline's first asset (a crate) seen from arm's length.
- What is in it: an orange wooden crate fills the frame, seen from above at close range. It has thick corner posts, plank lines and grey hex bolts. Three guns lie on the lid, each built from grey metal and orange parts. A dark workbench with more equipment is behind.

Properties worth matching:
1. **Every edge has a bevel that catches light.** The crate's corners and plank edges show as thin lighter lines. Without them the crate would be a flat orange rectangle.
2. **Chunky proportions.** Posts, bolts and planks are thicker than real ones. Nothing is thinner than a finger, so nothing flickers or vanishes at a distance.
3. **Two or three colours per object, repeated across objects.** Crate: orange and grey. Guns: grey and the same orange. The props belong together because they share a palette.
4. **Small parts are modelled, not painted.** Bolts, vents and grips are real geometry with their own light and shadow sides.
5. **Each material shows about three tones**: lit, shaded, and in shadow. That is enough to read the form.

Do not take: the faint painted streaks on the crate lid (a light wood-grain texture [observation]), which ADR 0007 rules out; and this is a posed promotional view, not a gameplay frame. Guns are also out of scope as subject matter; the lesson is the construction.

### 8. Ylands: cabin, log pile and anvil in snow

- Image: <https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/298610/ss_ab00899a466ad79be1e1083fa8349562c5bfc653.1920x1080.jpg> (local `08-ylands-cabin-snow.jpg`)
- Source page: Steam store page, <https://store.steampowered.com/app/298610/Ylands/>
- Owner: Bohemia Interactive (developer and publisher).
- Reference for: **building** and **props** in this style.
- What is in it: a timber A-frame cabin with crossed roof beams and a plank door on the left. In front: a character at an anvil on a stump, a campfire ringed with stones, a stack of cut logs with orange end grain, a bare bush. Behind: flat-faced green conifers and pale blue mountains in haze, with snow falling.

Why it matters: the store page says the game has "stunning low-poly visuals" and that players "construct anything" and "build your home". It is a shipped survival and building game in flat-colour low-poly.

Properties worth matching:
1. **Building pieces are plain colour blocks with visible thickness.** Beams, planks and roof panels are separate chunky parts, and you can see how the cabin was assembled.
2. **Cut ends are a different colour from sides.** The log ends are orange and the bark is grey. One colour change tells you the material with no texture.
3. **Faceted, not rounded.** Logs are six- or eight-sided, trees are stacked cones. The facets are part of the look, not a defect.
4. **Warm objects on a cool ground.** Wood and fire are orange; snow, sky and mountains are blue-white. The base stands out from the terrain.
5. **Distant mountains are two or three flat pale tones**, lighter with distance.

Do not take: the bright, cheerful, evenly lit daytime mood. It has no menace and little depth. Take the construction of the pieces, not the lighting. The character proportions are also not a reference (creatures and bodies are out of scope).

---

## 3. Runners-up

Kept locally in case the owner wants to swap one in. All were viewed; those marked (thumbnail) were judged at 600x338 only.

| # | Image | First-party page | Why it is here | Why it is not primary | Local file |
|---|-------|------------------|----------------|-----------------------|------------|
| 9 | [PEAK: figure before a tower in purple fog](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3527290/aa39b41b105aac51f2312a92979a3b9cb9909a46/ss_aa39b41b105aac51f2312a92979a3b9cb9909a46.1920x1080.jpg) | [Steam](https://store.steampowered.com/app/3527290/PEAK/) (Team PEAK; publishers listed as "Aggro Crab" and "Evil Landfall?") | One tiny figure, one huge tower, one fog colour over everything. The simplest scale picture found. A co-op climbing game. | Scale comes from looking **up** at a tower; the pit needs looking down. Cartoon characters. | `09-peak-tower-fog.jpg` |
| 10 | [Jusant: looking down a slope into blue haze](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1977170/ss_136f1aef35b769dea64a2b1f02f535d150b7c689.1920x1080.jpg) | [Steam](https://store.steampowered.com/app/1977170/Jusant/) (DON'T NOD) | The best "looking down from a height" frame: wooden walkways shrink below, far cliffs fade to pale blue. | Second image from one game; denser vegetation than our style allows. | `10-jusant-looking-down.jpg` |
| 11 | [Deep Rock Galactic: looking along a faceted shaft](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/548430/ss_1bc5367dbc85a91a08ec2846508c65a960dbd479.1920x1080.jpg) | [Steam](https://store.steampowered.com/app/548430/Deep_Rock_Galactic/) (Ghost Ship Games) | First-person view down a teal tunnel to a black hole, two small lit figures ahead. The flat faces of the terrain are very clear. | A gun and ammo counter fill the lower right. | `11-drg-shaft.jpg` |
| 12 | [Astroneer: base on a green planet](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/361420/ss_a1b3fd7d139ba491aba79a3731af0cf7dec04e0a.1920x1080.jpg) | [Steam](https://store.steampowered.com/app/361420/ASTRONEER/) (System Era Softworks) | Flat-colour modular base parts on flat-faced terrain. The store page says "objects are snapped into place in a modular system". | Seen from far above; white sci-fi kit; very saturated. Served at 1147x645. | `12-astroneer-base.jpg` |
| 13 | [*Made in Abyss*: looking up from inside](https://www.inspired.jp/wp/wp-content/uploads/2023/02/AB2_04_133_genzu-%EF%BD%942-1-%E3%81%AE%E3%82%B3%E3%83%94%E3%83%BC.jpg) | [Inspired gallery, "メイドインアビス017"](https://www.inspired.jp/gallery/page/7/) | Looking straight up a shaft at a ringed light, with jagged ledges pointing inward. The only "view up" found; relevant to **ascent**. | Very bright and washed out; a specific named place. | `13-mia-looking-up.jpg` |
| 14 | [Grow Home: looking down through vines to an island](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/323320/ss_0974926a9fa245a9329b5fcb4801202efc9d1b80.1920x1080.jpg) (thumbnail) | [Steam](https://store.steampowered.com/app/323320/Grow_Home/) (Reflections, a Ubisoft Studio) | A flat-shaded low-poly climbing game with great height; the ground is a small patch far below. | Bright toy-like colours, open sky, no fog to speak of. | `14-growhome-looking-down.jpg` |
| 15 | [Lonely Mountains: Downhill: canyon](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/711540/ss_02e45e1273dee428cdf2c83044372f0d60cb9664.1920x1080.jpg) | [Steam](https://store.steampowered.com/app/711540/Lonely_Mountains_Downhill/) (Megagon Industries) | Flat-faced orange cliff ledges with a gap between them: the clearest example of low-poly rock strata and overhangs. | Same game as pick 6; a faint grain on the rock. | `15-lmd-canyon.jpg` |

**Evaluated and rejected** (store screenshots viewed as contact sheets, nothing kept):

- **Valheim** (Iron Gate): good building and strong fog and light, but surfaces carry pixelated textures, which is a different style.
- **The Long Dark** (Hinterland): first-person and very atmospheric, but painted textures on every surface.
- **Firewatch** (Campo Santo): first-person with strong colour bands, but smooth, detailed models. Its layered-silhouette sunsets repeat the lesson of picks 2 and 3.
- **Journey** (thatgamecompany): superb fog and scale, but smooth sand and third-person; adds nothing picks 2 and 5 do not.
- **Sable** (Shedworks): flat colour with drawn outlines. Outlines are a different style decision (see owner question 6). One frame looking up a round brick shaft is worth a look if outlines are ever considered.
- **Risk of Rain 2** (Hopoo Games): all store frames are combat with heavy effects.
- **Cairn** (The Game Bakers): the most realistic climbing reference, but detailed textured rock.
- **White Knuckle** (Dark Machine Games): first-person climbing in a vertical shaft, the closest in subject. Its look is dark, grainy and retro-textured, which is the opposite of the chosen style. Useful later as a reference for how climbing looks from first person, not for style.
- **Aloft**, **Raft**: building games with detailed or painted surfaces.
- **Muck**: flat low-poly first-person survival, but flat lighting and no atmosphere. It shows what the style looks like when lighting and fog are **not** done, which is the failure the look test must avoid.
- **AER Memories of Old**, **The Witness**: attractive flat colour, but open sky and bright daylight; no depth or enclosure.

---

## 4. Draft style rules

These are the rules the eight picks share. They are a draft for the owner to accept or change, not a decision.

Every surface is one plain colour, and form is shown by flat faces and bevelled edges catching light, never by painted detail; a material should read from about three tones (lit, shaded, in shadow). Shapes are chunky, with nothing thinner than a finger, and each object has a silhouette that identifies it with all colour removed. Each layer has a palette of five to eight colours built on **two opposed colour families** (for example warm ground against cool distance) with one vivid accent that covers only a few per cent of the view; props and building pieces draw on the same palette as their layer so they belong to it. Distance is shown by fog alone: each step away loses contrast and drifts toward a single fog colour, pale on upper layers and dark on deep ones, until the far wall is a flat silhouette with roughly a quarter to a third of the near contrast. The bottom is never visible: a view down ends in cloud, haze or darkness. Light comes from few, clear sources with visible shafts or pools, and large parts of the frame may be left dark. Fine detail (flowers, bolts, small rocks) is spent only within a few metres of the player. Scale is always shown by something small and familiar placed far away: a figure, a ladder, a lamp, a building piece.

---

## 5. Tensions between the picks

The owner has to choose on each of these. The picks disagree, and the look test should be built to show both sides where practical.

1. **Hard flat faces or soft gradients.** Picks 4, 6 and 8 have sharp-edged flat faces. Pick 5 (Jusant) has smooth, rounded rock with gentle tone changes and looks the most polished of the games. ADR 0007 says flat-colour low-poly with bevels, which is the first group. If Jusant is what "beautiful" means to the owner, the ADR's style is the wrong one.
2. **Saturated or muted.** Deep Rock Galactic (4, 7) and Ylands (8) use strong, near-full-saturation colour. *Made in Abyss* (1 to 3) and Lonely Mountains (6) are muted, with one vivid accent. The paintings that inspired the game are on the muted side.
3. **Fog to pale or fog to dark.** Picks 2, 5 and 6 fade to a pale colour. Picks 3 and 4 fade to dark. Both work. A likely answer is pale near the rim and darker with each descent, but then deep layers lose long views, and with them the sense of scale.
4. **Painted source, flat-colour target.** Picks 1 to 3 get much of their beauty from brushwork: grass, leaves, rock grain. Flat colour cannot reproduce that. What carries over is palette, banding, fog and light. The owner should judge the look test on those four, and decide whether that is enough.
5. **Terrain faces: large and calm or small and busy.** Lonely Mountains uses big flat faces that look designed. Deep Rock Galactic's procedural terrain is many small triangles and looks noisier (see runner-up 11). The pit's terrain is procedural, so it will tend toward the second unless the generator is built to avoid it.
6. **Close or far.** The most beautiful flat-colour images (6, 8, 12) are seen from far away. The only good close-up (7) is a posed view from a game that also uses some painted texture. No first-party image found shows a pure flat-colour prop from 0.5 m in a first-person frame. This is the board's weakest point, and it is the exact condition ADR 0007 sets.
7. **Lit and readable or dark and menacing.** Pick 8 is bright and friendly; pick 4 is mostly black. A base must be readable to live in; the pit should feel dangerous. These pull in opposite directions inside one layer.

---

## 6. Questions for the owner

1. Looking only at picks 4 to 8: is any of them beautiful to you? If only pick 5 is, the flat-shaded style in ADR 0007 probably fails your condition before any asset is built.
2. Saturated like Deep Rock Galactic, or muted like Lonely Mountains and the *Made in Abyss* backgrounds?
3. Should fog get darker with each descent, so that deep layers show only what the player lights? Or should every layer keep at least one long view?
4. Is a faint texture or grain allowed (as on the crate in pick 7 and the rock in runner-up 15), or is "flat colour" strict?
5. How many colours may one layer's palette hold, and may a base use colours from outside its layer's palette so that it stands out?
6. Outlines (as in Sable) were not considered because ADR 0007 does not mention them. Should they stay out?
7. The look test needs a scale shot. Which view matters most: down from a ledge (picks 1, 5, runner-up 10), across to the far wall (pick 2), or up toward the rim (runner-up 13)?
8. Since no reference shows a flat-colour prop at 0.5 m, should the look test include a close-up of the first crate beside a 1.8 m figure, judged against pick 7, as its own pass or fail?
9. Which picks should be dropped or swapped for a runner-up before this board is used in reviews?

---

## 7. Method

- **Game images**: the screenshot lists were read from the Steam store API (`https://store.steampowered.com/api/appdetails?appids=<id>`), which returns the same images and description text as the store page. Twenty games were surveyed: the twelve named in the brief (Deep Rock Galactic, Astroneer, Valheim, Sable, Journey, Firewatch, Risk of Rain 2, Lonely Mountains: Downhill, The Long Dark, Jusant, Cairn, PEAK) plus The Witness, Grow Home, White Knuckle, Muck, Aloft, Raft, AER Memories of Old and Ylands. Up to 30 screenshots per game were viewed as contact sheets, then the shortlisted ones at full size.
- **Made in Abyss images**: the official anime site (<http://miabyss.com/>, gallery at <http://miabyss.com/gallery.html>) has only key art with characters and logos. The backgrounds come from the gallery of Inspired Inc. (<https://www.inspired.jp/gallery/>), which shows 40 backgrounds from the series and the film. Inspired states that it served as art director on the series ([Inspired, art book announcement, 2020](https://www.inspired.jp/2020/01/%E5%85%AC%E5%BC%8F%E3%82%A2%E3%83%BC%E3%83%88%E3%83%96%E3%83%83%E3%82%AF%E3%80%8E%E3%83%A1%E3%82%A4%E3%83%89%E3%82%A4%E3%83%B3%E3%82%A2%E3%83%93%E3%82%B9%E6%8E%A2%E7%AA%9F%E8%A8%98%E9%8C%B2%E3%80%8F/), read through a summarising fetch tool).
- **Palettes**: `magick <file> -resize 200x -colors 8 -unique-colors txt:` and the matching histogram, on the local copies. Seven colours are listed where the reduction returned seven.
- **Contrast and brightness numbers**: mean and standard deviation of greyscale, and mean saturation, on hand-placed rectangular crops (near, middle, far). The crops were chosen by eye, so treat the numbers as rough ratios, not measurements to match exactly.
- Steam image links are given without the `?t=` cache parameter; they resolved on the research date. Store screenshots are sometimes replaced, so a link may go dead; the local copy is the record.

---

## 8. Unverified items

- **Which layer of the source each *Made in Abyss* image shows.** The gallery titles are numbers only. Picks are described by what is visible, not by layer name.
- **The exact copyright holder of pick 3.** The gallery title names the film *Dawn of the Deep Soul*; the copyright line in the image is too small to read with confidence.
- **Inspired's art-director role** was read through a summarising fetch tool, not as raw page text.
- **Rendering techniques.** That Deep Rock Galactic's terrain is voxel-based and flat-shaded, that Jusant is smooth-shaded, that Lonely Mountains uses no textures, and which engine any of these games uses: none of this is stated on the store pages read. Every such statement here is marked [observation] and comes from looking at the images.
- **Whether picks 7 and 8 are unmodified gameplay frames.** Both look posed (no HUD, composed camera). They are official store screenshots, but may be promotional renders.
- **Grow Home's publisher.** Steam's data listed "Infogrames, Atari" as publisher on the fetch date, with Reflections, a Ubisoft Studio, as developer. Reported as returned; not checked further.
- No developer talk or art post-mortem was fetched for any game, so nothing here says **how** a look was made, only what it looks like.

## 9. Images wanted but not obtained from a first-party source

- **A flat-colour low-poly prop at about 0.5 m in a first-person gameplay frame.** Not found on any store page surveyed. Pick 7 is the closest and has the caveats listed.
- **A first-person view straight down a very deep shaft in a flat-colour game.** Runner-up 11 looks along a tunnel, not down a drop.
- **Player-built bases in Deep Rock Galactic's or Lonely Mountains' lighting.** Neither game has base building. The building references (8, 12) have weak atmosphere, so building and atmosphere are never shown together.
- **Clean, character-free *Made in Abyss* views from the rim, of the inverted forest and of the great fault, identified as such.** Inspired's gallery has unlabelled backgrounds that may be these. The official art book (*Made in Abyss* official art book, Takeshobo, named on Inspired's page above) would have labelled plates, but it is a printed book and was not consulted.
- **Press-kit versions of the game screenshots.** Only Steam store images were used. Developer press kits were not fetched and may hold cleaner or larger frames.
