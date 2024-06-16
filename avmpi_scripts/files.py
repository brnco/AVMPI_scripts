'''
object classes for files on disk
'''
import json
import logging
import pathlib


logger = logging.getLogger('main_logger')


def get_field_map(obj_type):
    '''
    returns dictionary of field mappings for Excel <-> BWF Metadata
    '''
    module_dirpath = pathlib.Path(__file__).parent.absolute()
    field_map_filepath = module_dirpath / 'field_mappings.json'
    with open(field_map_filepath, 'r') as field_map_file:
        field_mapping = json.load(field_map_file)
    return field_mapping[obj_type]


class BroadcastWaveFile(object):
    '''
    class for BWF WAVE

    BWF fields - required:
    Description
    Originator
    Origination Date
    Origination Time
    Originator Reference
    Version
    Coding History
    IARL
    ICOP
    ICRD
    INAM
    ITCH
    ISFT
    ISRC

    BWF fields - optional:
    UMID
    Time Reference
    ICMT
    IENG
    IKEY
    ISBJ
    ISRF
    '''
    def __init__(self, **kwargs):
        field_map = get_field_map('BroadcastWaveFile')
        required_fields = ['Description', 'Originator', 'originationDate',
                           'originationTime', 'originatorReference', 'Version',
                           'codingHistory', 'IARL', 'ICOP', 'ICRD', 'INAM',
                           'ITCH', 'ISFT', 'ISRC']
        optional_fields = ['UMID', 'timeReference', 'ICMT', 'IENG', 'IKEY',
                           'ISBJ', 'ISRF']
        for attr_name in required_fields:
            try:
                setattr(self, attr_name, kwargs[attr_name])
            except Exception as exc:
                pass
        for attr_name in optional_fields:
            try:
                setattr(self, attr_name, kwargs[attr_name])
            except Exception:
                pass

    @classmethod
    def from_xlsx(cls, row):
        '''
        creates BWF object from a row in Excel metadata template
        '''
        field_map = get_field_map('BroadcastWaveFile')
        instance = cls()
        for attr_name, mapping in field_map.items():
            try:
                column = mapping['xlsx']['column']
            except TypeError:
                column = mapping['xlsx']
            except Exception as exc:
                raise RuntimeError(exc)
            value = row[column]
            if not value:
                continue
            try:
                setattr(instance, attr_name, value)
            except Exception as exc:
                logger.error(f"attr_name: {attr_name}")
                logger.error(f"type(attr_name): {type(attr_name)}")
                logger.error(f"value: {value}")
                logger.error(f"type(value): {type(value)}")
                logger.error(exc, stack_info=True)
                raise RuntimeError("there was a problem parsing that value")
        return instance

    def to_bwf_meta_str(self):
        '''
        converts attributes into string that can be read by BWF MetaEdit
        '''
        bwf_meta_str = ''
        for attr_name, value in self.__dict__.items():
            chunk_str = '--' + attr_name + '="' + value + '" '
            bwf_meta_str += chunk_str
        return bwf_meta_str.strip()

    def to_bwf_meta_list(self):
        '''
        convert attributes into list for subprocess implementaiton of BWF MetaEdit
        '''
        bwf_meta_list = []
        for attr_name, value in self.__dict__.items():
            chunk_str = '--' + attr_name
            chunk = [chunk_str, value]
            bwf_meta_list.extend(chunk)
        return bwf_meta_list

