import re
from collections import defaultdict

class KeyAuditor:
    
    def __init__(self, xml_reader):
        self.xml_reader = xml_reader
        self.regex = {
            'lower': re.compile(r'^([a-z]|_|\-)*$'),
            'alphanum_colon': re.compile(r'^([\w]|_|\-)*:([\w]|_|\-)*$'),
            'double_colon': re.compile(r'^([A-Za-z0-9]|_)*:([A-Za-z0-9]|_)*:([A-Za-z0-9]|_)*$'),
            'problemchars': re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
        }

    def key_type(self, element, keys):
        if element.tag == "tag":
            if self.regex['lower'].search(element.attrib['k']):
                keys['lower'] += 1
            elif self.regex['alphanum_colon'].search(element.attrib['k']):
                keys['alphanum_colon'] += 1
            elif self.regex['double_colon'].search(element.attrib['k']):
                keys['double_colon'] += 1
            elif self.regex['problemchars'].search(element.attrib['k']):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
        return keys

    def test(self, filter_tags=None, limit=None):
        keys = defaultdict(int)
        for element in self.xml_reader.iterate(filter_tags=filter_tags, limit=limit):
            keys = self.key_type(element, keys)
        return keys


class StreetAuditor:

    def __init__(self, xml_reader):
        self.xml_reader = xml_reader
        self.prefix_streets = [
            'Sin', 'Ada', 'Alta', 'Ana', 'Blas', 'Bell', 'Cjal', 'Cmte', 'De', 'Del',
            'Cabo', 'Cap', 'Cnl', 'Tte', 'Carl', 'GRAL', 'GRL', 'Conc', 'Cruz', 'Cura',
            'Dip', 'Don', 'Diaz', 'Dirk', 'Eva', 'El', 'Ema', 'Emir', 'Emma', 'Enzo',
            'Ex', 'Fitz', 'Flor', 'John', 'Juez', 'La', 'Las', 'Leon', 'Los', 'Luis',
            'Lima', 'Lino', 'Lola', 'Lope', 'Mar', 'Olga', 'Olof', 'Paso', 'Paul', 'Pbro',
            'Palo', 'Paz', 'Pi', 'Pio', 'Plus', 'Raul', 'Rca', 'Rio', 'Rep', 'Ruiz',
            'Gdor', 'Gral', 'Grl', 'Igr', 'Ing', 'Jean', 'Juan', 'Hugo', 'Dr',
            'Ivan', 'Jose', 'Fray', 'Mons', 'San', 'Pte', 'Pres', 'Tcnl', 'Ruy', 'Sgt',
            'Sadi', 'Sir', 'Sor', 'Sta', 'Tgrl', 'Tuyu', 'Tres', 'Tula', 'Veva', 'Vito', 'Von',
            'Coronel', 'Carlos', 'Alberto', 'Almirante', 'Doctor', 'Domingo', 'Enrique',
            'Estanislao', 'Francisco', 'General', 'Gregorio', 'Intendente', 'José',
            'Manuel', 'Mariano', 'Martín', 'Padre', 'Pedro', 'Presidente',
            'Río', 'Ricardo', 'Santa', 'Teniente', 'Fragata', 'Eduardo', 'Esteban',
            'Emilio', 'Gaspar', 'Guillermo', 'Hipólito', 'Bernardo', 'Anatole', 'Antonio',
            'Aristóbulo', 'Acuña', 'Adolfo', 'Aguas', 'Agustín', 'Alejandro', 'Alférez',
            'Alfredo', 'Alicia', 'Amadeo', 'Amancio', 'Andrés', 'Andres', 'Antártida', 'Aristóbulo',
            'Avelino', 'Benito', 'Beron', 'Bahía', 'Bahia', 'Baldomero', 'Bartolomé',
            'Basilio', 'Batalla', 'Belisario', 'Antartida', 'Benjamín', 'Berón', 'Bernardino',
            'Bialet', 'Blanco', 'Bonifacio', 'Buenos', 'Camilo', 'Castro', 'Cañada', 'Benjamin',
            'Calderón', 'Capitán', 'Carolina', 'Cazadores', 'Cecilia', 'Cefiro', 'Ciudad', 'Claudio',
            'Colón', 'Coleta', 'Comandante', 'Combate', 'Comisionado', 'Comodoro', 'Concejal',
            'Concepción', 'Conquista', 'Costa', 'Cristóbal', 'Crisólogo', 'Cucha', 'Cornelio',
            'Cosme', 'Crisóstomo', 'Dámaso', 'Díaz', 'Dean', 'Deán', 'Diogenes', 'Dionisio',
            'Dante', 'Dardo', 'Diego', 'Diputado', 'Doctora', 'Elias', 'Elías', 'Elpidio',
            'Entre', 'Escalada', 'Estado', 'Estados', 'Eugenia', 'Eugenio', 'Aristobulo', 'Déan',
            'Feliciano', 'Felix', 'Florencio', 'Facundo', 'Federico', 'Felipe', 'Fernán', 'Fernando',
            'Florencia', 'Florentino', 'Gómez', 'Gervasio', 'Guidi', 'Guido', 'Gabriel', 'Gabriela',
            'Fernández', 'Gaetán', 'García', 'Godoy', 'Goncalvez', 'González', 'Grito', 'Guardia',
            'Hernando', 'Hipolito', 'Hernán', 'Heroes', 'Hilarión', 'Horacio', 'Humberto',
            'Ignacio', 'Arturo', 'Gobernador', 'Hermana', 'Ejército', 'Cristobal', 'Clemente',
            'Colorado', 'Combatientes', 'Ceferino', 'Centenario', 'Alvarez', 'Alvaro', 'Amado',
            'Achaval', 'Adrián', 'Agente', 'Aimé', 'Albarracín', 'Albert', 'Alfonsina', 'Alonso',
            'Amelia', 'Aníbal', 'Anselmo', 'Argentino', 'Arroyo', 'Arístides', 'Arzobispo', 'Arribeños',
            'Athos', 'Augustín', 'Aviador', 'Azucena', 'Baltasar', 'Barreiro', 'Bartolome', 'Bella',
            'Blasco', 'Bomberos', 'Boulogne', 'Brigadier', 'Cándido', 'Cátulo', 'César', 'Choele',
            'Caaguazú', 'Cabildante', 'Cabildo', 'Cacique', 'Callao', 'Campos', 'Canal', 'Capital',
            'Carmen', 'Carola', 'Casimiro', 'Catalina', 'Cayetano', 'Centenera', 'Cerro', 'Charcas',
            'Chile', 'Cláudio', 'Conejal', 'Conscripto', 'Corrales', 'Cristos', 'Cueli', 'Cupertino',
            'Curuz', 'Darregueira', 'Darwin', 'Delfín', 'Dellepiane', 'Diógenes', 'Duilio', 'Echeverria',
            'Ecuador', 'Edmundo', 'Elena', 'Eliseo', 'Curuzù', 'Constantino', 'Darragueira', 'Drago',
            'Emeric', 'Encarnación', 'Epidio', 'Ernesto', 'Escultor', 'Estanislao', 'Estero', 'Esteves',
            'Eustaquio', 'Evaristo', 'Ezequiel', 'Félix',
            'Gregoria', 'Gustavo', 'Ingeniero', 'Isabel', 'Jacinto', 'Jacobo', 'Joaquín',
            'Jorge', 'Josefina', 'Juana', 'Julián', 'Julian', 'Julio', 'Leandro', 'Leopoldo',
            'Lucio', 'Maestra', 'Maestro', 'María', 'Marcos', 'Mario', 'Mariquita', 'Mariscal',
            'Mayor', 'Mateo', 'Mercedes', 'Miguel', 'Monseñor', 'Montes', 'Ramón', 'Remedios',
            'República', 'Roberto', 'Rodrigo', 'Roque', 'Ruta', 'Sánchez', 'Santo', 'Santos',
            'Sargento', 'Teodoro', 'Tierra', 'Tomás', 'Franklin', 'Gerónimo', 'Germán',
            'Hilario', 'Justo', 'Maipú', 'Martin', 'Nicolás', 'Nemesio', 'Natalio', 'Martínez',
            'Leonardo', 'Olaguer', 'Olegario', 'Osvaldo', 'Pablo', 'Paraguay', 'Plaza', 'Posta',
            'Profesor', 'Rómulo', 'Recuero', 'Sáenz', 'Santiago', 'Subteniente', 'Giácomo', 'J', 'R',
            'Héctor', 'Mártires', 'Máximo', 'Méndez', 'Mahatma', 'Manuela', 'Martiniano', 'Nicanor',
            'Nueva', 'Paseo', 'Pastor', 'Patricias', 'Provincia', 'Puerto', 'Rafael', 'Rambla',
            'Ramos', 'Rodolfo', 'Rosario', 'Rufino', 'Ruperto', 'Salvador', 'Sebastián', 'Sebastian',
            'Segundo', 'Simón', 'Soldado', 'Hércules', 'Héroes', 'T', 'Túpac', 'Vélez', 'Víctor',
            'Vicente', 'Valentín', 'Ventura', 'Victoria', 'Virrey', 'Villa', 'Vuelta', 'William', 
            'Yerbal', 'Almte', 'Ángel', 'Abraham', 'Belgrano', 'Camila', 'León', 'Marcelo', 'Narsiso',
            'Reinalda', 'Silvio', 'Peatonal', 'Ayacucho', 'Sarmiento', 'Matheu', 'Colombia', 'Int',
            'Pueyrredón', 'Venezuela', 'Corrientes', 'Sanchez', 'Islas', 'Gorriti', 'Madame', 'Haedo', 'Garin',
            'Bonifacini', 'Saavedra', 'Caxaraville', 'Lincoln', 'Lavalle', 'Cnel', 'Velez', 'Sarandí', 'Puán',
            'Pío', 'Bombero', 'Chacabuco', 'Alvear', 'Perdriel', 'Independencia', 'Avellaneda', 'Castex', 'Rodríguez',
            'Viacava', 'Italia', 'Iturraspe', 'Juárez', 'Rosales', 'D´Onofrio', 'Indalecio', 'Rodríguez', 'Alianza',
            'Esposos', 'Progreso', 'Córdoba', 'Almafuerte', 'Rivadavia', 'América', 'Argentina', 'Industria',
            'Triunvirato', 'Wenceslao', 'Tandil', 'Ombú', 'Cuba', 'Reverenda', 'Senador', 'Asamblea', 'Sicilia',
            'Cuevas', 'Cerrito', 'Primera', 'Tucumán', 'Punta', 'Quirno', 'Saenz', 'Saturnino', 'Sitio', 'Marta',
            'Lisandro', 'Nicasio', 'Ministro', 'Gabino', 'Lomas', 'Victor', 'Valentin', 'Marco', 'Washington', 'Joaquin',
            "O'Donnell", 'O']

        self.street_type_re = re.compile(r'^\b(?P<stype>([^\W\d_]|´)+)\.?', re.IGNORECASE)
        self.street_words_re = re.compile(r'^\s*\S+(?:\s+\S+){1,}\s*$', re.IGNORECASE)
        self.abbreviated_name_re = re.compile(r'^[A-Z]\.\s')
        self.composite_number_name_re = re.compile(r'^([\d]+\s\-\s)(?P<stype>([^\W\d_]|´)+)\.?', re.IGNORECASE)
        self.composite2_number_name_re = re.compile(r'^(?P<stype>([^\W\d_]|´)+)\.?\s([\d]+\s\-\s)')
        self.date_names_re = re.compile(r'^[\d]{1,2}\sde\s', re.IGNORECASE)
        self.common_street_prefix_re = re.compile(r'^(%s)\s' % '|'.join(self.prefix_streets), re.IGNORECASE)
        self.expected = ["Avenida", "Boulevard", "Calle", "Pasaje", "Camino", "Acceso", "Autovía",
                         "Colectora", "Diagonal", "Ruta Nacional", "Ruta Provincial", 'Autopista']
        self.mapping = { "Av. ": "Avenida",
                         "Ave": "Avenida",
                         "Ave. ": "Avenida",
                         "Av ": "Avenida",
                         "AV ": "Avenida",
                         "av ": "Avenida",
                         "Au ": "Autopista",
                         "Avda ": "Avenida",
                         "Avda. ": "Avenida",
                         "BV ": "Boulevard",
                         "PJE ": "Pasaje",
                         "Pje. ": "Pasaje",
                         "Cno ": "Camino",
                         "Cno. ": "Camino",
                         "Cmno ": "Camino",
                         "Cno. ": "Camino",
                         "Diag ": "Diagonal",
                         "Diag. ": "Diagonal",
                         "RN ": "Ruta Nacional",
                         "RP ": "Ruta Provincial"}

    def audit_type(self, street_name):
        """
        Audits one street type and returns the corresponding string value

        TODO:
            - '316 - *Av.* 12 de Octubre'
        """
        street_name = street_name.strip()
        more_than_one_word = self.street_words_re.search(street_name)
        if not more_than_one_word:
            # assumed: Calle
            return 'Calle'
        date_names = self.date_names_re.search(street_name)
        if date_names:
            return 'Calle'
        abbreviated_name = self.abbreviated_name_re.search(street_name)
        if abbreviated_name:
            return 'Calle'
        composite_number_name = self.composite_number_name_re.search(street_name)
        if composite_number_name:
            street_type = composite_number_name.group('stype').strip().capitalize()
            if street_type not in self.prefix_streets:
                if street_type not in self.expected:
                    return street_type
                else:
                    return None
            else:
                return 'Calle'
        composite2_number_name = self.composite2_number_name_re.search(street_name)
        if composite2_number_name:
            street_type = composite2_number_name.group('stype').strip().capitalize()
            if street_type not in self.prefix_streets:
                if street_type not in self.expected:
                    return street_type
                else:
                    return None
            else:
                return 'Calle'
        common_street_prefix = self.common_street_prefix_re.search(street_name)
        if common_street_prefix:
            street_type = common_street_prefix.group().strip().capitalize()
            if street_type not in self.prefix_streets:
                if street_type not in self.expected:
                    return street_type
                else:
                    return None
            else:
                return 'Calle'
        m = self.street_type_re.search(street_name)
        if m:
            street_type = m.group('stype').strip().capitalize()
            if street_type not in self.prefix_streets:
                if street_type not in self.expected:
                    return street_type
                else:
                    return None  # correct street names are ignored here
        return 'Unknown'

    def audit_types(self, filter_tags=('node', 'way'), unknown=False):
        """
        Audits all street tags and adds types to a dictionary
        """
        street_types = defaultdict(set)
        elem_count = 0
        street_count = 0
        for elem in self.xml_reader.iterate(filter_tags=filter_tags):
            elem_count += 1
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    street_count += 1
                    street_type = self.audit_type(tag.attrib['v'])
                    include = set()
                    if street_type is not None and (unknown is True or street_type != 'Unknown'):
                        street_types[street_type].add(tag.attrib['v'])
        filtered = defaultdict(set)
        for stype in street_types:
            if len(street_types[stype]) > 1:
                filtered[stype] = street_types[stype]
        return {'elements': elem_count, 'streets': street_count, 'types': dict(filtered)}

    def update_name(self, name):
        for k in self.mapping:
            if re.search(k, name, re.IGNORECASE) and re.search(self.mapping[k], name) is None:
                name = re.sub(k, self.mapping[k]+' ', name, re.IGNORECASE)
        return name
