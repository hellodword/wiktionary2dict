# from mdict_utils.base.writemdict import MDictWriter

# dictionary = {
#     "doe": "a deer, a female deer.",
#     "0ray": "a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. ",
#     "far": "a long, long way to run.",
#     "me": "中文 麵麪麵 😀 😃 😄.",
#     "far2": "a long, long way to run.",
# }


# def test_mdict_writer():

#     writer = MDictWriter(
#         title="Example Dictionary",
#         description="This is an example dictionary.",
#         compression_type=2,
#         is_mdd=False,
#     )

#     writer._build_offset_table(dictionary)
#     writer._build_key_blocks()
#     writer._build_keyb_index()
#     writer._build_record_blocks()
#     writer._build_recordb_index()
#     with open('./data/sample.mdx', 'wb') as f:
#         writer.write(f)
