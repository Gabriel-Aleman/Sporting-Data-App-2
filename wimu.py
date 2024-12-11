from API_FrameWork import *
import pytz

# Define la zona horaria
zona_horaria = pytz.timezone('America/Costa_Rica')  # Puedes cambiar la zona horaria

# Obtén el Timestamp actual con la zona horaria
hoy = pd.Timestamp(datetime.now(tz=zona_horaria)).tz_localize(None)


tokenWimu= "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2NjkxMmRlNmVlNGQ3ZTM1NTIzYmZmMDciLCJjbHViIjoiNjQwZWVjOWE4NTY2ZDQxMmMyZTdlZGUyIiwiY2VudGVyIjoiNjQwZWVkMTE4NTY2ZDQxMmMyZTgxZWRiIiwidXNlclR5cGUiOiJDRU5URVJfQURNSU4iLCJ1c2VyIjoiNjY5MTJkZTZlZTRkN2UzNTUyM2JmZjA3IiwiZXhwIjoxNzM0NDQwMzM1fQ.My4K4JezASVS36X6CdifkeEqFaRmfA28O3oPp1Vt1PE"

headersWimu = {
    "accept": "application/json",
    "Authorization": f"Bearer {tokenWimu}"
}

urlsWimu ={
      "urlToken":       "https://wimupro.wimucloud.com/apis/rest/test", #Token
      "urlTeams":   "https://wimupro.wimucloud.com/apis/rest/teams",                                                #Equipos 
      "urlClub":    "https://wimupro.wimucloud.com/apis/rest/clubs"                                                 #Clubes
}


class myTeamAPIWimu(API):
    def __init__(self, header, urls, index=0):
        super().__init__(urls, header)
        self.tokenIsValid =self.checkAPI()
        self.inform = pd.read_excel("informe.xlsx", sheet_name="informe")
        self.session = pd.read_excel("informe.xlsx", sheet_name="listadoSesiones").set_index("id")
        self.getStyledInform() #Informe que se le muestra al ususario

    
        if self.tokenIsValid:
            #IDLE:
            self.getTeams() #Obtener la lista de equipos
            self.getClubs() #Obtener la lista de clubes
        
            if index==0:  #Predeterminado, escoger 1aM como mi equipo
                self.getMyTeam(id="640eed118566d412c2e81edb")
                
                self.getMyPlayers()
                self.jugXpos() 

    def checkAPI(self):
        response = requests.get(self.urls["urlToken"], headers=self.header)
        return (response.status_code == 200)        
    """
    getClubs: Método para obtener la lista de clubes matriculados.
    """
    def getClubs(self):
        self.Club = self.doRequest(self.urls["urlClub"])
    
        self.Club = [(i["id"], i["name"]) for i in self.Club]
        
        self.Club = pd.DataFrame(self.Club, columns=["id", "Nombre"])
        self.Club.set_index('id', inplace=True)

    """     
    getTeams: Método para obtener una lista de todos los equipos matriculados asociados.
    """
    def getTeams(self):
        self.teams = self.doRequest(self.urls["urlTeams"])
        
        self.teams = [(i["id"], i["name"], i["abbreviation"])  for i in self.teams]
        
        self.teams = pd.DataFrame(self.teams, columns=["id", "Nombre", "Abreviatura"])
        self.teams.set_index('id', inplace=True)
    
    """
    getMyTeam: Método para escoger el equipo del que me interesa obtener los resultados basado en 
    el criterio de mi escogencia.
    inputs:
        -index: Indice númeral del equipo que me interesa.
        -name Nombre del equipo que me interesa.
        -abv: Abreviatura del equipo que me interesa.
        -id: Id del equipo que me interesa.
    """
    def getMyTeam(self, index=None, name=None, abv=None, id=None):

        if (index is not None):
            self.myTeam = self.teams.iloc[index]
            self.myTeam = self.myTeam.name 
            
        elif (name is not None):
            self.myTeam = self.teams.query(f"Nombre == '{name}'")
            self.myTeam = self.myTeam.iloc[0].name
            
        elif (abv is not None):
            self.myTeam = self.teams.query(f"Abreviatura == '{abv}'")
            self.myTeam = self.myTeam.iloc[0].name
                        
        elif (id is not None):
            self.myTeam = self.teams.loc[id]
            self.myTeam = self.myTeam.name 
        
        self.urls["urlPlayers"] = f"https://wimupro.wimucloud.com/apis/rest/players?team={self.myTeam}&page=1&limit=200&sort=name%2Casc"
        

    """
    getMyPlayers: Método para obtener el listado con los jugadores del equipo que escogí.
    """
    def getMyPlayers(self):
        self.players  = self.doRequest(self.urls["urlPlayers"])
        
        self.players  = [(i["id"], i["name"], i["lastName"], i["height"], i["weight"], i["position"], i["maxSpeed"], i["maxAcc"], i["maxHR"]) for i in self.players]
        self.players  = pd.DataFrame(self.players, columns=["id", "Nombre", "Apellido", "Altura (m)", "Peso (kg)","Posición", "máx Vel", "máx Ac", "máx HR"])
        self.players.set_index('id', inplace=True)

        self.players['Posición'] = self.players['Posición'].replace(['VOLANTE OFENSIVO', 'Volante ofensivo', 'Volante defensivo', 'Volante mixto', 'VOLANTE DEFENSIVO'], "Volante")
        self.players['Posición'] = self.players['Posición'].replace([""], "Sin datos de posicicón")
        self.jugXpos()
        
    """
    getAllSessions: M´étodo para btener un listado con todas las sesiones registradas.
    inputs:
        -limit: Límite de datos por página
        -sort: Criterio de ordenación (ascendente o descentendte)
        -onlyColective: Si se desean solo resultados de las sesiones colectivas
        -fromYearStart: Si se desean solo las sesiones desde comienzos de este año.
        -playersAsName: Si se desea ver los jugadores según su nombre en lugar de según si id.
    """
    def getAllSessions(self, type=None):
        if type == "fromYearStart":
            myDate = pd.Timestamp(datetime(hoy.year, 1, 1))
        elif type == "fromMonthAgo":
            myDate = hoy - pd.DateOffset(months=1)
        else:
            myDate = None

        #Se puede ordenar las sesiones empezando por la última (predeterminado) o la primera
        sortType = "end,desc" 
        self.myUrl = "https://wimupro.wimucloud.com/apis/rest/sessions"

        self.parameters ={
            "team": self.myTeam,
            "informTypes": "intervalsindoor",
            "page": 1,
            "limit": 200,
            "sort": sortType
        }
        
        self.session = self.findMyPagedResultsCompress(myDate)
            
        self.session = self.session [["id","name", "created", "duration", "group", "matchDay", "weekCalendar", "members", "sessionTasks"]]
        self.session.columns      = ["id", "Nombre" , "Creado", "Duración (min)", "Grupo" , "matchDay" , "semanaCal" ,"Participantes" , "Actividades de la sesión"]
    
        self.session.set_index('id', inplace=True)
        self.session["Duración (min)"] = self.session["Duración (min)"].apply(milliseconds_to_minutes) #Obtener duración de la sesión en minutos

        #Solo sesiones colectivas
        self.session = self.session.query('Grupo == "Collective"')
        self.session.drop(['Grupo'], axis=1, inplace=True)


       #ATLETAS POR NOMBRE EN LUGAR DE ID:
       #--------------------------------------------------------------
        a=self.session["Participantes"].tolist()
        temArr=[]
        for i in a:
            try:
                tempVar=self.players.loc[i]
            except KeyError:
                pass
                temArr0=[]
                
                for j in i:
                    try:
                        tempVar0=self.players.loc[j]
                    except KeyError:
                        temArr0.append(f"{j} Not Found in players")
                    else:
                        b=tempVar0["Nombre"]+" "+tempVar0["Apellido"]
                        temArr0.append(b)
                temArr.append(temArr0)
            else:
                b=tempVar["Nombre"]+" "+tempVar["Apellido"]
                temArr.append(b.tolist())
        self.session["Participantes"] = temArr
       #--------------------------------------------------------------
    
        #Evitar que 2 o más sesiones tengan el mismo nombre
        conteo = self.session['Nombre'].value_counts()
        duplicados = conteo[conteo > 1].index

        for valor in duplicados:
            mask = self.session['Nombre'] == valor
            counts = self.session[mask].groupby('Nombre').cumcount() + 1
            self.session.loc[mask, 'Nombre'] = self.session.loc[mask, 'Nombre'] + ' _ ' + counts.astype(str)

        if not(myDate):
            myDate =  self.session["Creado"].iloc[-1]
            
        return myDate
    """
    getSessionAssistants: Método para obtener un listado de los jugadores que asistieron a determinada sesión.
    -input:
        -filter: Si el dato ya está filtrado o no
    """
    def getSessionAssistants(self, filter=True):
        a= "Miembros" if filter else "members"
        return self.players.loc[self.mySession[a]]
    
    """
    getMySession: Selecionar una sesión especifica
    -input:
        -index: Indice de la sesión (de 0 a n)
        -name: Nombre de la sesión.
        -id:   Id de la sesión
    """
    def getMySession(self, index=None, name=None, id=None):        
        if(index is not None):
            self.mySession = self.session.iloc[index]
        
        elif(name is not None):
            self.mySession = self.session.query('Nombre == @name').iloc[0]
            
        elif(id is not None):
            self.mySession = self.session.loc[id]
  
    """
    getInform: Generar el informe completo de una sesión con los resultados que nos interesan.
    inputs: 
        -sort: Criterio de ordenación (ascendente o descendente)
        -sessionId: Id de la sesión de la que queremos el reporte.
        -nameSes: Nombre de la sesión de la que queremos el reporte.
        -onlyOneSes: Variable booleana que determina si es solo 1 sesión
    output: 
        -self.inform: Informe de la sesión correspondiente.
    """
    def getInform(self,sort=True, sessionId=None, nameSes=None, onlyOneSes=False):

        self.mySession = self.session.loc[sessionId] if (sessionId is not None) else self.session.query('Nombre == @nameSes').iloc[0] if (nameSes is not None) else None

        self.myUrl=self.urls["urlInform"] ="https://wimupro.wimucloud.com/apis/rest/informs"
        
        sortType = "end,desc" if sort else "start,asc"
        
        print("Descargando SESIÓN:",self.mySession["Nombre"])
        
        self.parameters = {
            "task": "Drills",
            "session": self.mySession.name,
            "informTypes": "intervalsindoor",
            "page": 1,
            "limit": 200,
            "team": self.myTeam,
            "sort": sortType
        }

        self.inform= self.doRequest()
        data =                                   [(j["id"],self.mySession["Nombre"], j["created"]    , j["username"], j["duration"]   , j["distance"]["distance"],j["distance"]["HSRAbsDistance"],j["accelerations"]["highIntensityAccAbsCounter"],j["accelerations"]["highIntensityDecAbsCounter"]) for j in self.inform]
        self.inform = pd.DataFrame(data, columns=['id'    , "Sesión",'Creado (fecha)', "Jugador"  , "Duración (min)", "Distancia m",            "HSRAbsDistance",               "highIntensityAccAbsCounter"                    ,"highIntensityDecAbsCounter"])
        

        self.inform["Duración (min)"] = self.inform["Duración (min)"].apply(milliseconds_to_minutes) 
        self.inform["Creado (fecha)"] =	self.inform["Creado (fecha)"].apply(getMyDate)
        self.inform['Creado (fecha)'] = self.inform['Creado (fecha)'].dt.strftime('%Y-%m-%d %H h : %M min')  # Formato YYYY-MM-DD

        if onlyOneSes:
            self.inform.drop(columns=["Sesión"], inplace=True)
        return self.inform
        
    """
    getAllInforms: Obtener un listado que integre todas las sesiones.
    inputs: 
        -myRange: Indicarle si queremos solo las "n" últimas sesiones en el informe completo.
        -beginDate: Fecha a partir de la cual quiero los datos
        -endDate: Fecha a partir de la cual ya no quiero los datos.
    """
    def getAllInforms_V3(self, range=None, mySesList=None):
        self.myUrl = "https://wimupro.wimucloud.com/apis/rest/informs"

        mySessions = self.session if not(mySesList) else mySesList

        informe=[]
        
        numSes=len(mySessions)
        for i, sesion in enumerate(mySessions.index):
            
            print(f"Generando informe {i}")
            if(i==range):
                break
            self.parameters = {
                "task": "Drills",
                "session": sesion,
                "informTypes": "intervalsindoor",
                "page": 1,
                "limit": 200,
                "team": self.myTeam,
                "sort":  "end,desc"
            }

            inform= self.doRequest()
            inform =                                   [(k["id"],  k["created"], sesion, k["username"], k["duration"], k["distance"]["distance"], k["distance"]["HSRAbsDistance"], k["sprint"]["distance"], k["sprint"]["maxSpeed"],k["accelerations"]["highIntensityAccAbsCounter"],k["accelerations"]["highIntensityDecAbsCounter"]) for k in inform]
            informe.extend(inform)
            print(round(i/numSes, 3))
        self.df             = pd.DataFrame(informe, columns=["id","Fecha","Sesión", "Jugador", "Duración", "Distancia total", "HSR", "SPRINT", "Velocidad máxima", "HSR dist", "acc", "dec"])
        self.df["Fecha"]    = pd.to_datetime(self.df['Fecha'], unit='ms')
        self.df["Fecha"]    = self.df['Fecha'].dt.strftime("%Y-%m-%d %H:%M")
        self.df["Duración"] = self.df["Duración"]/60000
        self.df["Duración"] = self.df["Duración"].astype("int")

        if mySesList is None:
            self.inform = self.df
    


    """
    getZScores: Método para obtener el parametro z del informe completo
    -inputs:
        -data: Define si quiero organizar mi tabla con z score  por sesión o jugador.

    -outputs:
        -c : Z score x sesión o jugador
        -cP: Z score promedio por sesión o jugador
    """
    def getZScores(self):
        lista = self.listaJugadores if (self.data=="Jugador") else self.listaSesiones if(self.data=="Sesión") else None
        c=self.compInformByXData.copy()
        c.drop(columns=["Duración (min)", "Creado (fecha)"], inplace=True)
        c.columns = [i+ "- Z score" for i in c.columns]

        templist=[]
        templiswimuApp=[]

        for element in lista:                                   #Iterar sobre cada sesión o jugador
            m = c.loc[element]
            m = (m - m.mean()) / m.std()                       #Calcula z score

            m["Sesión"]=[element]*len(m)
            m.set_index(["Sesión"], append=True, inplace=True)
            m=m.swaplevel(0, 1)
            m['Z score Average'] = m.mean(axis=1)              #Promedio de los z scores x línea
            templiswimuApp.append(m['Z score Average'].mean()) #Promedio x sesión
            templist.append(m)


        # Concatenar las nuevas columnas con el DataFrame original
        c = pd.concat(templist)
        c["Creado (fecha)"] = self.compInformByXData["Creado (fecha)"].to_list()
        columnas = ['Creado (fecha)'] + [col for col in c.columns if col != 'Creado (fecha)']
        c = c[columnas]
                                        
        cP = pd.DataFrame(templiswimuApp, columns=["Promedios Z score"])                 #cP:Matriz con el promedio de los z score
        cP.index = lista

        return c, cP

    def findNewSes(self):
        self.nuevasSesiones = np.setdiff1d(self.session.index, self.inform["Sesión"])
       
    def getStyledInform(self, inf=None):
        if inf is None:
            self.styledInform = self.inform.copy()
        else:
            self.styledInform = inf
        self.styledInform["Sesión"]     = self.session.loc[self.styledInform["Sesión"].to_list()]["Nombre"] .to_list()
        self.styledInform.drop(["id"], axis=1, inplace=True)
    
    def ses_play(self):
        self.infxPlay=self.styledInform.set_index(["Jugador", "Sesión" ])
        self.infxPlay.sort_values(by="Jugador", inplace=True)
        self.infxSes=self.styledInform.set_index(["Sesión", "Jugador"])
        self.infxSes.sort_values(by="Sesión", inplace=True)
    def jugXpos(self):
        self.jugxPos={}
        for pos in self.players["Posición"]:
            jugNom=self.players.query("Posición == @pos")[["Nombre", "Apellido"]]
            jugNom["Nombre completo"] = jugNom["Nombre"]+" "+jugNom["Apellido"] 
            jugNom=jugNom["Nombre completo"].to_list()
            self.jugxPos[pos]=jugNom
    def jugXpos_filter(self, pos):
        if(pos)!= "Todos":
            self.styledInform=self.styledInform[self.styledInform['Jugador'].isin(self.jugxPos["Delantero"])]
        else:
            self.getStyledInform()

    def infXMD(self, MD):
        if(MD)!= "Todos":
            MD=self.session.query('matchDay == @MD')
            #Lista de sesiones en el informe que fueron un MD
            MD_Filter=np.intersect1d(pd.unique(self.inform["Sesión"]), MD.index)
            inf_Filter=self.inform[self.inform["Sesión"].isin(MD_Filter)]
            self.getStyledInform(inf_Filter)
        else:
            self.getStyledInform()

wimuApp= myTeamAPIWimu(header=headersWimu, urls=urlsWimu) #Crear objeto con la clase
