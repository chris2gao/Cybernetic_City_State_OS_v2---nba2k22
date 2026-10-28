"""Read-data catalog and one facade; missing fields remain explicit coverage gaps."""
import json
from dataclasses import dataclass
from pathlib import Path
from facade import NativeControlFacade
@dataclass(frozen=True)
class NativeReadQuery:
 dataset_id:str
 parameters:dict
 request_id:str=''
class NativeReadCatalog:
 def __init__(self,path=None):self.data=json.loads(Path(path or Path(__file__).parent/'data/read_catalog.json').read_text(encoding='utf-8'))
 def list(self):return self.data['datasets']
 def get(self,dataset_id):
  return next(r for r in self.data['datasets'] if r['dataset_id']==dataset_id)
class NativeReadFacade:
 def __init__(self,control=None,catalog=None):self.control=control or NativeControlFacade();self.catalog=catalog or NativeReadCatalog()
 def read(self,query:NativeReadQuery):
  dataset=self.catalog.get(query.dataset_id)
  # Catalog lookup is inert; a supplied transport is used only for this explicit call.
  if query.dataset_id=='player.editor_state':
   from player_editor_state import validate_projection
   if not isinstance(query.parameters,dict):raise ValueError('Exact Player read parameters required')
   validate_projection(self.control.registry.root,query.parameters.get('projection'))
  return self.control.read(dataset['action_id'],query.parameters,request_id=query.request_id)
