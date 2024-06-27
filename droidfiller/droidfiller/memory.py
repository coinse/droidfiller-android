from .config import agent_config
import chromadb
chroma_client = chromadb.Client()

class Memory:
    def __init__(self, name, profile):
        self.memory = chroma_client.create_collection(name=name)
        self.memory_entry_id = 0
        self.adopt_persona(profile)
        self.add_entry(f"I am a new user for {agent_config.app_description}, named '{agent_config.app_name}'.", "SELF_DESCRIPTION")
        self.add_entry("I am trying to explore its functionalities based on my own interests.", "INTENT")

    def adopt_persona(self, profile):
        residence_information = {}
        for l in profile.strip().split('\n'):
            if len(l.strip()) == 0:
                continue
            prop = l.strip().removeprefix("-").strip()
            if ':' not in prop:
                continue
            prop_name = prop.split(':')[0].strip()
            prop_value = prop.split(':')[1].strip()

            if prop_name in ['self_introduction', 'app_usage_pattern']:
                self.add_entry(prop_value, "SELF_DESCRIPTION")
            elif prop_name in ['personality']:
                continue
            elif prop_name in ['city', 'state', 'country']:
                residence_information[prop_name] = prop_value
                if prop_name == 'country':
                    if len(residence_information) > 0:
                        self.add_entry(f"I live in {residence_information['city']}, {residence_information['state']} in {residence_information['country']}", "SELF_DESCRIPTION")
            else:
                prop_name = prop_name.replace('_', ' ')
                if prop_name == 'phone':
                    prop_name = 'phone number'
                self.add_entry(f"My {prop_name} is {prop_value}", "SELF_DESCRIPTION")
        
            
    def get_entry(self, entry_id):
        entry = self.memory.get(ids=[str(entry_id)])
        if len(entry['documents']) == 0:
            return None, None
        return entry['documents'][0], entry['metadatas'][0]

    def add_entry(self, description, type, tag='', backlink=''):
        self.memory_entry_id += 1
        self.memory.add(
            documents=[description.strip()],
            metadatas=[{"type": type, "backlink": backlink, "tag": tag}],
            ids=[str(self.memory_entry_id)]
        )
        return str(self.memory_entry_id)

    def add_action(self, description, backlink=''):
        return self.add_entry(description, "ACTION", backlink=backlink)
    
    def add_plan(self, description):
        return self.add_entry(description, "PLAN")

    def add_intent(self, description):
        return self.add_entry(description, "INTENT")

    def add_observation(self, description, backlink='', tag='CURRENT_PAGE'): # possible tags: CURRENT_PAGE, NEW_PAGE
        return self.add_entry(description.strip(), "OBSERVATION", 
        backlink=backlink, tag=tag)

    def add_reflection(self, description, backlink=''):
        return self.add_entry(description, 'REFLECTION', backlink=backlink)

    def get_entries_after(self, entry_id):
        entry_id = int(entry_id)
        raw_entries = self.memory.get()
        entries = []
        for memory_id, metadata, doc in zip(raw_entries['ids'], raw_entries['metadatas'], raw_entries['documents']):
            if int(memory_id) > entry_id:
                entries.append(self.__stringify_entry(memory_id, metadata, doc, show_id=False))
        entries.sort(key=lambda x: x[0])
        memory_str = ''
        for memory_id, entry in entries:
            memory_str += entry

        return memory_str.strip()

    def get_entries_before(self, entry_id):
        entry_id = int(entry_id)
        raw_entries = self.memory.get()
        entries = []
        for memory_id, metadata, doc in zip(raw_entries['ids'], raw_entries['metadatas'], raw_entries['documents']):
            if int(memory_id) < entry_id:
                entries.append(self.__stringify_entry(memory_id, metadata, doc, show_id=False))
        entries.sort(key=lambda x: x[0])
        memory_str = ''
        for memory_id, entry in entries:
            memory_str += entry

        return memory_str.strip()

    def __str__(self):
        raw_entries = self.memory.get()
        
        return self.__stringify(raw_entries)

    def __stringify_entry(self, memory_id, metadata, doc, show_id=True):
        if metadata['type'] == 'OBSERVATION':
            if metadata['tag'] == 'CURRENT_PAGE':
                doc = f'{doc}'
            elif metadata['tag'] == 'NEW_PAGE':
                doc = f'(New page) {doc}'
        
        doc = f'[{metadata["type"]}] {doc}\n'

        if show_id:
            return (int(memory_id), f'<{memory_id}> {doc}')
        else:
            return (int(memory_id), doc)


    def __stringify(self, raw_entries, show_id=True):
        entries = []
        for memory_id, metadata, doc in zip(raw_entries['ids'], raw_entries['metadatas'], raw_entries['documents']):
            entries.append(self.__stringify_entry(memory_id, metadata, doc, show_id=show_id))

        entries.sort(key=lambda x: x[0])
        entries = entries[max(-100, -len(entries)):]
        
        memory_str = ''
        for memory_id, entry in entries:
            memory_str += entry

        return memory_str.strip()
