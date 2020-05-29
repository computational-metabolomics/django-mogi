from sitetree.utils import tree, item

# Be sure you defined `sitetrees` in your module.
sitetrees = (
  # Standard tree for mogi tools
  tree('mogi_all', items=[
      # Then define items and their children with `item` function.
      item('MOGI', 'mogi.idetail', children=[
          item('Upload ISA project to Galaxy data library', 'galaxy_isa_upload_datalib', in_menu=True, in_sitetree=True),
          item('Upload ISA project to Galaxy history', 'galaxy_isa_upload_history', in_menu=True, in_sitetree=True),
          item('Upload ISA data files to Galaxy data library', 'galaxy_isa_fileselect_upload_datalib', in_menu=True, in_sitetree=True),
          item('Upload ISA data files to Galaxy history', 'galaxy_isa_fileselect_upload_history', in_menu=True, in_sitetree=True),
          item('View & Run Workflows', 'isa_workflow_summary', in_menu=True, in_sitetree=True),

      ])
  ]),
 # Trees for the whole MOGI project
 tree('dma', items=[
      # Then define items and their children with `item` function.
      item('DMA', 'init1', children=[
          item('DMA init project', 'init1', in_menu=True, in_sitetree=True),

      ])
  ]),

  tree('isa', items=[
      # Then define items and their children with `item` function.
      item('ISA', 'ilist', children=[
          item('View all ISA projects', 'ilist', in_menu=True, in_sitetree=True),
          item('Create investigation', 'icreate', in_menu=True, in_sitetree=True),
          item('Create study', 'screate', in_menu=True, in_sitetree=True),
          item('Create assay', 'acreate', in_menu=True, in_sitetree=True),
          item('Create study sample', 'smcreate', in_menu=True, in_sitetree=True),
          item('Create study factor', 'sfcreate', in_menu=True, in_sitetree=True),
          item('View ISA data files', 'view_isa_data_files', in_menu=True, in_sitetree=True),
      ])
  ]),

  tree('galaxy', items=[
      # Then define items and their children with `item` function.
      item('Galaxy', 'history_status', children=[

          item('Register Galaxy instance', 'addgi', in_menu=True, in_sitetree=True),
          item('Register Galaxy user', 'addguser', in_menu=True, in_sitetree=True),
          item('Upload ISA project to Galaxy data library', 'galaxy_isa_upload_datalib', in_menu=True, in_sitetree=True),
          item('Upload ISA data files to Galaxy data library', 'galaxy_isa_fileselect_upload_datalib', in_menu=True, in_sitetree=True),
          item('View & Run Workflows', 'isa_workflow_summary', in_menu=True, in_sitetree=True),
          item('History status', 'history_mogi', in_menu=True, in_sitetree=True),

      ])
  ]),


  tree('view', items=[
      # Then define items and their children with `item` function.
      item('View', 'cpeakgroupmeta_summary', children=[
          item('Show all metabolomics files', 'mfile_summary', in_menu=True, in_sitetree=True),
          item('Show LC-MS datasets', 'cpeakgroupmeta_summary', in_menu=True, in_sitetree=True)
      ])
  ]),

  tree('search', items=[
      # Then define items and their children with `item` function.
      item('Search', 'init1', children=[
          item('Summary', 'search_summary',  in_menu=True, in_sitetree=True),
          item('Fragmentation search', 'search_frag',  in_menu=True, in_sitetree=True),
          item('Search m/z', 'search_mz',  in_menu=True, in_sitetree=True),
          item('Search neutral mass', 'search_nm',  in_menu=True, in_sitetree=True),
      ])
  ])

  # ... You can define more than one tree for your app.
)