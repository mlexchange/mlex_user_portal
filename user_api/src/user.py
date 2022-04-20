import uuid as UUIDf
from neo4j import GraphDatabase, basic_auth

class userAPI:

    def __init__(self, url, auth):
        self.url     = url
        self.auth    = auth
        self.driver  = GraphDatabase.driver(url, auth=basic_auth(self.auth[0], self.auth[1]))
        self.session = self.driver.session()

    ### ROLES ###
    def create_role(self, role):
        """ Create a role node. """
        parameters = {'role': role}
        cquery = '''
        CALL {
            MATCH (r:Role {name:$role})
            RETURN count(r) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts > 0,
            'RETURN toInteger(0) AS result',
            'MERGE (r:Role:Attribute {name:role}) RETURN toInteger(1) AS result',
            {counts:counts, role:$role}) YIELD value
        RETURN value.result as results        
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('results') > 0:
            status = print("New " + str(role) + " role was created!")
        else:
            status = print("[WARNING] New role '" + str(role) + "' was not created. Role already exists.")
        return status

    def delete_role(self, role):
        """ Delete a role node. """
        parameters = {'role': role}
        cquery = '''
        CALL {
            MATCH (r:Role {name:$role})
            DETACH DELETE r
            RETURN r
        }
        WITH MATCH (r:Role {name:$role})
        RETURN toInteger(counts(r)) AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data().get('result')
        if result == 0:
            status = print("The " + str(role) + " was removed from the database.")
        else:
            status = print("[WARNING] The " + str(role) + " still exists in the database.")
        return status

    def add_user_to_role(self, uuid, role):
        """ Assigns a user to a role. """
        parameters = {'uuid': uuid, 'role': role}
        cquery = '''
        MATCH (r:Role {name:$role})
        CALL {
            MATCH (u:user {uuid:$uuid})-[rel:has_attr]->(role:Role:Attribute)
            DELETE rel
            RETURN u
        }
        WITH u, r 
        MERGE (u)-[rel:has_attr]->(r)
        RETURN toInteger(count(rel)) AS result
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('result') > 0:
            status = print("User " + str(uuid) + " now has the " + str(role) + " role.")
        else:
            status = print("[WARNING] User " + str(uuid) + " role was not updated.")
        return status

    def remove_user_from_role(self, uuid, role):
        """ Removes a role of a user and sets user role to Unapproved. """
        parameters = {'uuid': uuid, 'role': role}
        cquery = '''
        MATCH (u:user {uuid: $uuid})-[rel:has_attr]->(r:Role {name:$role})
        DELETE rel
        WITH MATCH (u), (role:Role {name:'Unapproved'})
        MERGE (u)-[:has_attr]->(role)
        RETURN u.uuid
        '''
        user_id = self.session.run(cquery, parameters=parameters)
        status = print("User " + str(user_id) + " has been removed from the " + str(role) + " and is now an Unapproved user.")
        return status

    ### USERS ###
    def create_user(self, fname, lname, email, orcid):
        """ A function to add user node. Every user is assigned as Unapproved after sign-up. """
        test_query = '''
        MATCH (up:UserProfile {fname:$fname, lname:$lname, email:$email, orcid:$orcid})
        RETURN count(up) as counts
        '''
        counts = self.session.run(test_query, parameters={'fname':fname, 'lname':lname, 'email':email, 'orcid':orcid}).data()
        if counts[0].get('counts') > 0:
            status = print('User already exists. Have user ask admin for support.')
        else:
            cquery = '''
            match (u:user) return u
            '''
            dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
            temp_id = 'u_' + str(fname[0] + lname + str(dbindx).zfill(5))
            
            parameters = {'temp_id': temp_id, 'fname': fname, 'lname': lname, 'email': email, 'orcid': orcid, 'role': 'Unapproved'}
            cquery = '''
            MATCH (r:Role {name:$role})
            MERGE (up:UserProfile:Object 
            {fname: $fname, lname: $lname, email: $email, orcid: $orcid, uuid: $temp_id, active:True})<-[:owner_of]-(u:Subject:user:Primitive {uuid: $temp_id})-[:has_attr]->(r)
            SET u.active = True
            RETURN u.uuid AS userid
            '''
            user_id = self.session.run(cquery, parameters=parameters).data()
            if user_id:
                status = print("Account with user_id " + str(user_id[0].get('userid')) + " has been created!")
            else:
                status = print("[WARNING] An error occurred during user creation.")
        return status
    
    def archive_user(self, uuid):
        ''' Remove user from active user database and archive the uuid with its relationships to its owned assets. '''
        parameters = {'uuid': uuid}
        cquery = '''
        CALL {
            MATCH (up:UserProfile {uuid: $uuid})-[rel:has_attr]->()
            SET up.active = False
            RETURN rel AS rels
            UNION ALL
            MATCH (u:user {uuid: $uuid})-[rel:has_attr]->()
            SET u.active = False
            RETURN rel AS rels
        }
        WITH count(rels) AS counts, rels
        CALL apoc.do.when(counts = 0,
            'RETURN toInteger(1) AS result',
            'DELETE rels RETURN toInteger(0) AS result',
            {counts:counts, rels:rels}) YIELD value
        RETURN value.result AS activity
        '''
        activity = self.session.run(cquery, parameters=parameters).data()
        if activity is True:
            status = print("[WARNING] User " + str(uuid) + " is still active.")
        else:
            status = print("Account of " + str(uuid) + " has been set to inactive.")
        return status
    
    ### COMPUTE LOCATIONS ###
    def create_compute(self, name:str, hostname:str, public=True, uuid:str=None):
        """
        Create a compute location node. Name and location must uniquely define compute.
        """
        if public:
            parameters = {'name': name, 'hostname': hostname}
            cquery = '''
            CALL {
                MATCH (cl:Compute {name:$name, hostname:$hostname})
                RETURN count(cl) AS counts
                }
            WITH counts, $name AS cl_name, $hostname AS cl_hostname
            CALL apoc.do.when(counts > 0,
                'RETURN toInteger(0) AS result',
                'MATCH (pub:Public) MERGE (comp:Compute:Object {name:cl_name, hostname:cl_hostname})-[:has_attr]->(pub) RETURN toInteger(1) AS result',
                {counts:counts, cl_name:cl_name, cl_hostname:cl_hostname}) YIELD value
            RETURN value.result as result
            '''
            index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        else:
            parameters = {'uuid':uuid, 'name': name, 'hostname': hostname}
            cquery = '''
            CALL {
                MATCH (cl:Compute {name:$name, hostname:$hostname})
                RETURN count(cl) AS counts
                }
            WITH counts, $name AS cl_name, $hostname AS cl_hostname, $uuid AS user_id
            CALL apoc.do.when(counts > 0,
                'RETURN toInteger(0) AS result',
                'MATCH (u:user {uuid:user_id}) MERGE (comp:Compute:Object {name:cl_name, hostname:cl_hostname})<-[:owner_of]-(u) RETURN toInteger(1) AS result',
                {counts:counts, cl_name:cl_name, cl_hostname:cl_hostname, user_id:user_id}) YIELD value
            RETURN value.result as result
            '''
            index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] Compute location was not created. Please choose a different name and/or location to successfully create.") 
        else:
            status = print("Compute location has been created!")
        return status

    def delete_compute(self, name:str, hostname:str):
        """
        Deletes a compute location node and confirms the action. For admins only.
        """
        parameters = {'name': name, 'hostname':hostname}
        cquery = '''
        CALL {
            MATCH (cl:Compute {name:$name, hostname:$hostname})
            DETACH DELETE (cl)
            }
        MATCH (cl:Compute {name:$name, hostname:$hostname})
        RETURN count(cl) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("[WARNING] Compute location either was not removed or a duplicate exists.")
        else:
            status = print("Compute location with hostname " + str(hostname) + " either has been deleted or does not exist.")
        return status
    
    def add_user_to_compute(self, uuid:str, cname:str, chostname:str):
        ''' Assigns a user to a compute location. '''
        parameters = {'uuid': uuid, 'cname': cname, 'chostname':chostname}
        cquery = '''
        MATCH (u:user {uuid:$uuid}), (cl:Compute {name:$cname, hostname:$chostname})
        MERGE (u)-[relat:user_of]->(cl)
        RETURN count(relat) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("User " + str(uuid) + " now has access to compute location " + str(chostname) + ".")
        else:
            status = print("[WARNING] User " + str(uuid) + " access to compute location " +str(chostname) + " was not updated.")
        return status

    def remove_user_from_compute(self, uuid:str, cname:str, chostname:str):
        ''' Removes a user from compute location. '''
        parameters = {'uuid': uuid, 'cname': cname, 'chostname':chostname}
        cquery = '''
        MATCH (u:user {uuid:$uuid})-[rel:user_of]->(cl:Compute {name:$cname, hostname:$chostname})
        WITH rel, count(rel) as counts
        CALL apoc.do.when(counts > 0,
            'DELETE rel RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {rel:rel, counts:counts}) YIELD value
        RETURN value.result AS result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User " + str(uuid) + " access to compute hostname " +str(chostname) + " was not updated.")
        else:
            status = print("User " + str(uuid) + " has been removed from access to compute hostname " + str(chostname) + ".")
        return status
    
    ### TEAMS ###
    def create_team(self, name:str, owner:str):
        """ Create a team. Owner and admin access. """
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        CALL {
            MATCH (t:Team {name: $name, owner: $owner})
            RETURN count(t) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts = 0,
            'MATCH (u:user {uuid:$owner}) MERGE (u)-[:owner_of]->(n:Team:Attribute:Group {name: $name, owner: $owner}) RETURN toInteger(1) AS result',
            'RETURN toInteger(0) as result',
            {owner:$owner, name:$name}) YIELD value
        RETURN value.result AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if result == 0:
            status = print('[WARNING] User has already created a team with this name. Please use a different name.')
        else:
            status = print("Team " + str(name) + " has been successfully created.")
        return status

    def delete_team(self, name:str, owner:str):
        """ Delete team. Only owner or admin access. """
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        CALL {
            MATCH (t:Team {name:$name, owner:$owner})
            RETURN count(t) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts = 0,
            'RETURN toInteger(0) as result',
            'MATCH (t:Team {name:$name, owner:$owner}) DETACH DELETE t RETURN toInteger(1) AS result',
            {owner:$owner, name:$name}) YIELD value
        RETURN value.result AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if result == 0:
            status = print("[WARNING] User did not create a team called " + str(name) + ". Please use a different name.")
        else:
            status = print("Team " + str(name) + " was deleted from the database.")
        return status


    def add_user_to_team(self, uuid:str, tname:str, towner:str):
        """ Assign a user to a team. Restricted to admins and team owner."""
        parameters = {'uuid': uuid, 'tname': tname, 'towner':towner}
        cquery = '''
        MATCH (u:user {uuid:$uuid}), (t:Team {name:$tname, owner:$towner})
        MERGE (u)-[relat:has_attr]->(t)
        RETURN count(relat) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("User " + str(uuid) + " is now a member of " + str(towner) + "'s "+ str(tname) + ".")
        else:
            status = print("[WARNING] User " + str(uuid) + " membership to " + str(tname) + " was not updated.")
        return status

    def remove_user_from_team(self, uuid:str, tname:str, towner:str):
        ''' This method is to remove a user from a team. '''
        parameters = {'uuid': uuid, 'tname': tname, 'towner':towner}
        cquery = '''
        MATCH (u:user {uuid:$uuid})-[rel:has_attr]->(t:Team {name:$tname, owner:$towner})
        WITH rel, count(rel) as counts
        CALL apoc.do.when(counts > 0,
            'DELETE rel RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {rel:rel, counts:counts}) YIELD value
        RETURN value.result AS result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User " + str(uuid) + " membership for " + str(towner) + "'s " + str(tname) + " was not updated.")
        else:
            status = print("User " + str(uuid) + " has been removed from " + str(towner) + "'s " + str(tname) + ".")
        return status

    ### CONTENT (MLExchange-Hosted Assets) and USER (unhosted, private) ASSETS ###
    def create_user_asset(self, name:str, owner:str, type:str, path:str, public=False):
        ''' Adds a customizable user asset after checking for existance of duplicates. Transaction-locked query.'''
        parameters = {'name': name, 'owner': owner, 'path': path, 'type': type}
        if public:
            cquery = '''
            CALL {
                    MATCH (ua:UserAsset {name:$name, owner:$owner, path:$path, type:$type})
                    RETURN count(ua) AS counts
                }

            WITH counts
            CALL apoc.do.when(counts = 0,
                'CREATE (ua:UserAsset:Object:Primitive {uauid: toString((name)+toString(timestamp()))}) RETURN ua.uauid AS result',
                '',
                {counts:counts, name:$name}) YIELD value

            WITH value.result as ua_uid
            MATCH (u:user {uuid: $owner}), (ua:UserAsset {uauid:ua_uid}), (pub:Public {name:'Public'})
            CREATE (u)-[:owner_of]->(ua)-[:has_attr]->(pub)
            SET ua.name = $name, ua.owner = $owner, ua.path = $path, ua.type = $type
            RETURN ua_uid
            '''
        else:
            cquery = '''
            CALL {
                    MATCH (ua:UserAsset {name:$name, owner:$owner, path:$path, type:$type})
                    RETURN count(ua) AS counts
                }

            WITH counts
            CALL apoc.do.when(counts = 0,
                'CREATE (ua:UserAsset:Object:Primitive {uauid: toString((name)+toString(timestamp()))}) RETURN ua.uauid AS result',
                '',
                {counts:counts, name:$name}) YIELD value

            WITH value.result as ua_uid
            MATCH (u:user {uuid: $owner}), (ua:UserAsset {uauid:ua_uid})
            CREATE (u)-[:owner_of]->(ua)
            SET ua.name = $name, ua.owner = $owner, ua.path = $path, ua.type = $type
            RETURN ua_uid
            '''
        
        ua_uid = self.session.run(cquery, parameters=parameters).data()
        if ua_uid:
            status = print("User Asset ID " + str(ua_uid[0].get('ua_uid')) + " has been created!")
        else:
            status = print("[WARNING] User asset was not created.")
        return status
    
    def create_content_asset(self, name:str, owner:str, type:str, cuid:str, public=False):
        ''' Registers creation of new assets from content registry. Transaction-locked query.'''
        parameters = {'name': name, 'owner': owner, 'type': type, 'cuid':cuid}
        if public:
            cquery = '''
            CALL {
                MATCH (ca:content {cuid:$cuid})
                RETURN count(ca) AS counts
            }
                        
            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid}), (pub:Public {name:'Public'})
            SET ca.name = $name, ca.owner = $owner, ca.type = $type
            CREATE (u)-[:owner_of]->(ca)-[:has_attr]->(pub)            
            RETURN ca.cuid as cauid
            '''
            ca_uid = self.session.run(cquery, parameters=parameters).data()
            if ca_uid:
                status = print("Public-flagged MLExchange Content has been registered: ID " + str(ca_uid[0].get('cauid')))
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " already has been registered. Contact Content Registry admin.")
        else:
            cquery = '''
            CALL {
                MATCH (ca:content {cuid:$cuid})
                RETURN count(ca) AS counts
            }
            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid})
            CREATE (u)-[:owner_of]->(ca)
            SET ca.name = $name, ca.owner = $owner, ca.type = $type
            RETURN ca.cuid as cauid
            '''
            ca_uid = self.session.run(cquery, parameters=parameters).data()
            if ca_uid:
                status = print("Private-flagged MLExchange Content has been registered: ID " + str(ca_uid[0].get('cauid')))
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " already has been registered. Contact Content Registry admin.")
        return status

    def delete_user_asset(self, uauid=None, owner=None):
        """ Deletes user asset from graph database. Function for owner. """
        parameters = {'owner': owner, 'uauid': uauid}
        cquery = '''
        MATCH (ua:UserAsset {owner:$owner, uauid:$uauid})
        WITH count(ua) AS counts
        CALL apoc.do.when(counts > 0,
            'MATCH (ua:UserAsset {owner:$ua_owner, uauid:$ua_uid}) DETACH DELETE (ua) RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {counts:counts, ua_owner:$owner, ua_uid:$uauid}) YIELD value
        RETURN value.result as result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User Asset ID " + str(uauid) + " was not deleted.")
        if index == 1:
            status = print("User Asset ID " + str(uauid) + " has been removed from the database.")
        else:
            status = print("[WARNING] User Asset ID " + str(uauid) + " could not be found in database. Verify ID and try again.")
        return status
    
    def delete_content_asset(self, cuid=None):
        """ Deletes content asset from graph database. Function for Compute API, owner, and admin. """
        if cuid:
            parameters = {'cuid':cuid}
            cquery = '''
            MATCH (ca:content {cuid:$cuid})
            WITH count(ca) AS counts
            CALL apoc.do.when(counts > 0,
                'MATCH (c:content {cuid:$c_uid}) DETACH DELETE (c) RETURN toInteger(1) AS result',
                'RETURN toInteger(0) AS result',
                {counts:counts, c_uid:$cuid}) YIELD value
            RETURN value.result as result
            '''
            index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
            if index == 0:
                status = print("[WARNING] Content ID " + str(cuid) + " was not deleted.")
            if index == 1:
                status = print("Content ID " + str(cuid) + " has been removed from the Content Registry.")
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " could not be found in database. Verify ID and try again.")
        return status

    ### GET COMMANDS FOR RETRIEVING STORED DATABASE INFORMATION ###
    def get_userdb_metadata(self, active=True):
        """ Gets all information on active users (default). When "active" is false, returns ALL users. """
        if active:
            cquery = '''
            MATCH (up:UserProfile {active:True})
            RETURN up
            '''
            status = self.session.run(cquery).data()
        else:
            cquery = '''
            MATCH (up:UserProfile)
            RETURN up
            '''
            status = self.session.run(cquery).data()
        return [s['up'] for s in status]

    def get_members_for_team(self, tname:str, towner:str):
        """ Gets all members for a select team. """
        parameters = {'tname':tname, 'towner':towner} 
        cquery = '''
        MATCH (t:Team {name:$tname, owner:$towner})<-[rel:has_attr]-(u:user)-[:owner_of]->(up:UserProfile)
        WITH count(rel) AS counts, t, up, u
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Member" AS result',
                {counts:counts}) YIELD value
        RETURN up.fname AS fname, up.lname AS lname, up.email AS email, value.result AS membership
        UNION
        MATCH (t:Team {name:$tname, owner:$towner})<-[rel:manager_of]-(u:user)-[:owner_of]->(up:UserProfile)
        WITH count(rel) AS counts, t, up, u
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Manager" AS result',
                {counts:counts}) YIELD value
        RETURN up.fname AS fname, up.lname AS lname, up.email AS email, value.result AS membership
        UNION
        MATCH (t:Team {name:$tname, owner:$towner})<-[rel:owner_of]-(u:user)-[:owner_of]->(up:UserProfile)
        WITH count(rel) AS counts, t, up, u
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Owner" AS result',
                {counts:counts}) YIELD value
        RETURN up.fname AS fname, up.lname AS lname, up.email AS email, value.result AS membership
        '''
        mem_team_dict = self.session.run(cquery,parameters=parameters).data()
        return mem_team_dict

    def get_metadata_for_user(self, uuid:str):
        """ Returns single user's metadata. """
        cquery = '''
        MATCH (up:UserProfile {uuid:$uuid})
        RETURN up
        '''
        status = self.session.run(cquery, parameters={'uuid':uuid}).data()
        return [s['up'] for s in status]

    def get_all_assets(self):
        cquery = '''
        MATCH (ca:content)
        RETURN ca AS asset
        UNION ALL
        MATCH (ua:UserAsset)
        RETURN ua AS asset
        '''
        status = self.session.run(cquery).data()
        return [s['asset'] for s in status]

    # def get_assets_for_user(self, uuid:str):
    #     cquery = '''
    #     MATCH (ca:content)
    #     RETURN ca AS asset
    #     UNION ALL
    #     MATCH (ua:UserAsset)
    #     RETURN ua AS asset
    #     '''
    #     status = self.session.run(cquery).data()
    #     return [s['asset'] for s in status]

    def get_all_roles(self):
        cquery = '''
        match (r:Role)
        return r
        '''
        status = self.session.run(cquery).data()
        return [s['r'] for s in status]

    def get_all_compute(self):
        cquery = '''
        match (comp:Compute)
        return comp
        '''
        status = self.session.run(cquery).data()
        return [s['comp'] for s in status]
    
    def get_compute_for_user(self, uuid:str):
        """ Get all compute locations that a single user can access. """
        parameters = {'uuid':uuid}
        cquery = '''
        match (comp:Compute)<-[:user_of]-(u:user {uuid:$uuid})
        return comp
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        return [s['comp'] for s in status]

    def get_all_teams(self):
        cquery = '''
        match (t:Team)
        return t
        '''
        status = self.session.run(cquery).data()
        return [s['t'] for s in status]

    def get_teams_for_user(self, uuid:str, owned_only=False):
        parameters = {'uuid':uuid}
        if owned_only:
            cquery = '''
            MATCH (t:Team {owner:$uuid})
            RETURN t.name AS tname
            '''
            teams_list = self.session.run(cquery,parameters=parameters).data()
            return [t['tname'] for t in teams_list]
        else:
            cquery = '''
            MATCH (u:user {uuid:$uuid})-[rel:has_attr]->(t:Team)<-[own_01:owner_of]-(u_01:user)-[own_02:owner_of]->(up:UserProfile)
            WITH count(rel) AS counts, t, up, u_01
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Member" AS result',
                {counts:counts}) YIELD value
            RETURN t.name AS tname, t.owner AS towner, up.fname AS towner_fname, up.lname AS towner_lname, value.result AS membership
            UNION
            MATCH (u:user {uuid:$uuid})-[rel:owner_of]->(t:Team)
            WITH count(rel) AS counts, t, u
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Owner" AS result',
                {counts:counts}) YIELD value
            RETURN t.name AS tname, t.owner AS towner, '' AS towner_fname, '' AS towner_lname, value.result AS membership
            UNION
            MATCH (u:user {uuid:$uuid})-[rel:manager_of]->(t:Team)<-[own_01:owner_of]-(u_01:user)-[own_02:owner_of]->(up:UserProfile)
            WITH count(rel) AS counts, t, up, u_01
            CALL apoc.do.when(counts <> 1,
                '',
                'RETURN "Manager" AS result',
                {counts:counts}) YIELD value
            RETURN t.name AS tname, t.owner AS towner, up.fname AS towner_fname, up.lname AS towner_lname, value.result AS membership
            '''
            teams_dict = self.session.run(cquery,parameters=parameters).data()
            return teams_dict

    def get_uuid_from_email(self, email:str):
        ''' Uses an email to retrieve a uuid. '''
        parameters={'email':email}
        cquery = '''
        MATCH (u:user)-[:owner_of]->(up:UserProfile {email:$email})
        RETURN u.uuid AS uuid
        '''
        uuid = self.session.run(cquery, parameters=parameters).data()[0]['uuid']
        print(uuid)
        return uuid

    def get_users(self, key_value):
        ''' This method will get all users including their profiles.
            The key will filter out irrelevant users.
            e.g. key = {'fname': 'Noah'} will return all users with Noah as their first name. '''
        
        key_value = {k: v for k, v in key_value.items() if v is not None}

        cquery = '''
        match (up:UserProfile)
        return up
        '''
        status = self.session.run(cquery).data()

        # Filter users based on the key_value filter, only active users
        users = []
        if key_value:
            for user in status:
                if user['up']['active']:
                    truth = True
                    for k, v in key_value.items():
                        if user['up'][k] != v: 
                            truth = False
                            break
                
                if truth: users.append(user['up'])
            
        else:
            for user in status:
                if user['up']['active']: users.append(user['up'])

        return users

    def create_action(self):
        cquery = '''
        merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
        '''
        status = self.session.run(cquery)
        return status
        
    # Make policies
    def create_new_policy(self, subject_dict, object_dict, action, policy_owner, policy_name):
        '''
        subject_dict = {'Team': ('name', 'MLEx_Team')}
        object_dict = {'Asset': ('name', 'asdf')}
        '''
        # Check if the policy_owner has authority (i.e. admin)
        # Perhaps, we need to find several roles with one cypher query call in the next version.
        parameters = {'uuid': policy_owner, 'role': 'Admin'}
        cquery = '''
        match (u:user {uuid: $uuid})-[:has_attr]->(r:Role {name: $role})
        return r
        '''
        status1 = self.session.run(cquery, parameters=parameters).data()
        
        parameters = {'uuid': policy_owner, 'role': 'MLE Admin'}
        cquery = '''
        match (u:user {uuid: $uuid})-[:has_attr]->(r:Role {name: $role})
        return r
        '''
        status2 = self.session.run(cquery, parameters=parameters).data()
        
        if not (len(status1) or len(status2)):
            msg = 'Can\'t create policy. The user is not an authorized user.'
            raise NotImplementedError(msg)

        # Check whether action is valid.
        if action not in ['Read', 'Full Access']:
            msg = ValueError('The action is not available')
            raise msg

        ''' Check if subject and object exist. '''
        sub_key = list(subject_dict.keys())[0]
        sub_val = subject_dict[sub_key] 
        obj_key = list(object_dict.keys())[0]
        obj_val = object_dict[obj_key]

        # Check if the owner has the policy already, if not, policy is created.
        # If the policy doesn't exist, then create a policy.
        parameters = {'uuid': policy_owner, 'policy_name': policy_name}
        cquery = '''
        match (u:user {uuid: $uuid})-[:owner_of]->(p:Policy {name: $policy_name})
        return p
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if len(status):
            msg = 'The policy is already been created. Please give different name.'
            raise ValueError(msg)

        # Check if the object belongs to the owner
        parameters = {'uuid': policy_owner, 'obj_val1': obj_val[1]}
        cquery1 = "match (u:user {uuid: $uuid})"
        cquery2 = f'(o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}-[r:owner_of]->{cquery2}
        return r
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The asset/content doesn\'t belong to the user'
            raise ValueError(msg)

        # Create a relationship between owner and policy.
        parameters = {'uuid': policy_owner, 'policy_name': policy_name}
        cquery = '''
        match (u:user {uuid: $uuid})
        merge (u)-[:owner_of]->(p:Policy {name: $policy_name, decision: "Permit"})
        '''
        status = self.session.run(cquery, parameters=parameters).data()

        # Create policy, i.e. sub_con, obj_con, and act_con
        parameters = {'sub_val1': sub_val[1], 'obj_val1': obj_val[1], 'policy_name': policy_name}
        cquery1 = f'match (s:{sub_key} ' + '{' + f'{sub_val[0]}:' + '$sub_val1})'
        cquery2 = f'match (o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}
        {cquery2}
        return s, o
        '''
        status = self.session.run(cquery, parameters=parameters).data()[0]

        if not (status['s'] and status['o']):
            msg = ValueError('The subject and/or object node(s) doesn\'t exist')
            raise msg
        cquery3 = 'match (fullAccess:Attribute:Group {name:"Full Access"})'
        cquery4 = 'match (pol:Policy {name: $policy_name})'
        cquery = f'''
        {cquery1}
        {cquery2}
        {cquery3}
        {cquery4}
        merge (pol)<-[:SUB_CON]-(s)
        merge (pol)<-[:OBJ_CON]-(o)
        merge (pol)<-[:ACT_CON]-(fullAccess)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    def check_policy_owner_relation(self, policy_owner, policy_name):
        ''' Check if the policy owns by the policy's owner '''
        parameters = {'uuid': policy_owner, 'policy_name': policy_name}
        cquery = '''
        match (u:user {uuid: $uuid})-[r:owner_of]->(p:Policy {name: $policy_name})
        return u, r, p
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        truth = []

        if len(status):
            t1 = status[0]['u']['uuid'] == policy_owner
            t2 = status[0]['r'][1] == 'owner_of'
            t3 = status[0]['p']['name'] == policy_name
            t = [t1, t2, t3]
        
        return t

    def add_subject_to_policy(self, subject_dict, policy_owner, policy_name):
        sub_key = list(subject_dict.keys())[0]
        sub_val = subject_dict[sub_key] 
        
        # check if subject exists
        parameters = {'sub_val1': sub_val[1]}
        cquery1 = f'match (s:{sub_key} ' + '{' + f'{sub_val[0]}:' + '$sub_val1})'
        cquery = f'''
        {cquery1}
        return s
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The subject doesn\'t exists'
            raise ValueError(msg)

        # check policy owner and policy relation
        t = self.check_policy_owner_relation(policy_owner, policy_name)
        if not t[0]:
            msg = 'The owner doesn\'t exist'
            raise ValueError(msg)
        if not t[1]:
            msg = 'The user doesn\'t own the policy'
            raise ValueError(msg)
        if not t[2]:
            msg = 'The policy doesn\'t exist'
            raise ValueError(msg)
        
        parameters = {'sub_val1': sub_val[1], 'policy_name': policy_name}
        cquery1 = f'match (s:{sub_key} ' + '{' + f'{sub_val[0]}:' + '$sub_val1})'
        cquery2 = 'match (pol:Policy {name: $policy_name})'
        cquery = f'''
        {cquery1}
        {cquery2}
        merge (pol)<-[:SUB_CON]-(s)
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        
        return status

    def remove_subject_from_policy(self, subject_dict, policy_owner, policy_name):
        sub_key = list(subject_dict.keys())[0]
        sub_val = subject_dict[sub_key] 
        
        # check if subject exists
        parameters = {'sub_val1': sub_val[1]}
        cquery1 = f'match (s:{sub_key} ' + '{' + f'{sub_val[0]}:' + '$sub_val1})'
        cquery = f'''
        {cquery1}
        return s
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The subject doesn\'t exists'
            raise ValueError(msg)
        
        # check policy owner and policy relation
        t = self.check_policy_owner_relation(policy_owner, policy_name)
        if not t[0]:
            msg = 'The owner doesn\'t exist'
            raise ValueError(msg)
        if not t[1]:
            msg = 'The user doesn\'t own the policy'
            raise ValueError(msg)
        if not t[2]:
            msg = 'The policy doesn\'t exist'
            raise ValueError(msg)

        parameters = {'sub_val1': sub_val[1], 'policy_name': policy_name}
        cquery1 = f'(s:{sub_key} ' + '{' + f'{sub_val[0]}:' + '$sub_val1})'
        cquery2 = '(pol:Policy {name: $policy_name})'
        cquery = f'''
        match {cquery2}<-[rel:SUB_CON]-{cquery1}
        detach delete rel
        '''
        status = self.session.run(cquery, parameters=parameters).data()

        return status

    def add_object_to_policy(self, object_dict, policy_owner, policy_name):
        obj_key = list(object_dict.keys())[0]
        obj_val = object_dict[obj_key]
        
        # check if object exists
        parameters = {'obj_val1': obj_val[1]}
        cquery1 = f'match (o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}
        return o
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The object doesn\'t exists'
            raise ValueError(msg)

        # check policy owner and policy relation
        t = self.check_policy_owner_relation(policy_owner, policy_name)
        if not t[0]:
            msg = 'The owner doesn\'t exist'
            raise ValueError(msg)
        if not t[1]:
            msg = 'The user doesn\'t own the policy'
            raise ValueError(msg)
        if not t[2]:
            msg = 'The policy doesn\'t exist'
            raise ValueError(msg)

        # check object owner relation
        parameters = {'uuid': policy_owner, 'obj_val1': obj_val[1]}
        cquery1 = "match (u:user {uuid: $uuid})"
        cquery2 = f'(o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}-[r:owner_of]->{cquery2}
        return r
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The asset/content doesn\'t belong to the user'
            raise ValueError(msg)

        # Create the object policy relationship
        parameters = {'obj_val1': obj_val[1], 'policy_name': policy_name}
        cquery1 = f'match (o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery2 = 'match (pol:Policy {name: $policy_name})'
        cquery = f'''
        {cquery1}
        {cquery2}
        merge (pol)<-[:OBJ_CON]-(o)
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        
        return status

    def remove_object_from_policy(self, object_dict, policy_owner, policy_name):
        obj_key = list(object_dict.keys())[0]
        obj_val = object_dict[obj_key] 
        
        # check if object exists
        parameters = {'obj_val1': obj_val[1]}
        cquery1 = f'match (o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}
        return o
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The object doesn\'t exists'
            raise ValueError(msg)
        
        # check policy owner and policy relation
        t = self.check_policy_owner_relation(policy_owner, policy_name)
        if not t[0]:
            msg = 'The owner doesn\'t exist'
            raise ValueError(msg)
        if not t[1]:
            msg = 'The user doesn\'t own the policy'
            raise ValueError(msg)
        if not t[2]:
            msg = 'The policy doesn\'t exist'
            raise ValueError(msg)

        # check object owner relation
        parameters = {'uuid': policy_owner, 'obj_val1': obj_val[1]}
        cquery1 = "match (u:user {uuid: $uuid})"
        cquery2 = f'(o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery = f'''
        {cquery1}-[r:owner_of]->{cquery2}
        return r
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The asset/content doesn\'t belong to the user'
            raise ValueError(msg)

        parameters = {'obj_val1': obj_val[1], 'policy_name': policy_name}
        cquery1 = f'(o:{obj_key} ' + '{' + f'{obj_val[0]}:' + '$obj_val1})'
        cquery2 = '(pol:Policy {name: $policy_name})'
        cquery = f'''
        match {cquery2}<-[rel:OBJ_CON]-{cquery1}
        detach delete rel
        '''
        status = self.session.run(cquery, parameters=parameters).data()

        return status
        
    def change_action_policy(self, action, policy_owner, policy_name):
        # check policy owner and policy relation
        t = self.check_policy_owner_relation(policy_owner, policy_name)
        if not t[0]:
            msg = 'The owner doesn\'t exist'
            raise ValueError(msg)
        if not t[1]:
            msg = 'The user doesn\'t own the policy'
            raise ValueError(msg)
        if not t[2]:
            msg = 'The policy doesn\'t exist'
            raise ValueError(msg)

        # Check previous action
        parameters = {'policy_name': policy_name}
        if action == 'Read':
            cquery0 = "match (pol:Policy {name: $policy_name})<-[rel:ACT_CON]-(fullAccess:Attribute:Group {name:'Full Access'})"
            cquery1 = "match (act:Action {name:'Read'})"
        else:
            cquery0 = "match (pol:Policy {name: $policy_name})<-[rel:ACT_CON]-(read:Action {name:'Read'})"
            cquery1 = "match (act:Attribute:Group {name:'Full Access'})"
        cquery = f'''
        {cquery0}
        return rel
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if not len(status):
            msg = 'The action that can\'t be changed due to no relationship found.'
            raise ValueError(msg)
        
        cquery = f'''
        {cquery0}
        {cquery1}
        detach delete rel
        merge (pol)<-[:ACT_CON]-(act)
        '''
        status = self.session.run(cquery, parameters=parameters)

        return status

    def delete_policy(self, policy_owner, policy_name):
        parameters = {'uuid': policy_owner, 'name': policy_name}
        cquery = '''
        match (u:user {uuid: $uuid})-[:owner_of]->(p:Policy {name: $name})
        //detach delete p
        return u, p
        '''
        status = self.session.run(cquery, parameters=parameters).data()
        if len(status):
            user = status[0]['u']
            policy = status[0]['p']
            if not policy:
                msg = 'The policy doesn\'t exist'
                raise ValueError(msg)
        else:
            msg = 'The user and/or the policy don\'t exist'
            raise ValueError(msg)
               
        parameters = {'uuid': policy_owner, 'name': policy_name}
        cquery = '''
        match (u:user {uuid: $uuid})-[:owner_of]->(p:Policy {name: $name})
        detach delete p
        return u, p
        '''
        status = self.session.run(cquery, parameters=parameters).data()

        return status


    # Make policies
    # test_policy1 and test_policy2 are depreciated. They will be deleted in the next update.
    def test_policy1(self):
        ''' Admin have full access ALL database objects and assets. '''
        cquery = '''
        /// Policy 1 - Admin has full access to UserProfiles, Content Assets, User Assets, Computing Resources 
        match (admin:Role {name: 'Admin'})
        match (up:UserProfile), (ca:content), (ua:UserAsset), (comp:Compute)
        match (act:fullAccess {name:"Full Access"})
        create (pol:Policy {name: 'Policy1', decision: 'Permit'})
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:OBJ_CON]-(up)
        merge (pol)<-[:OBJ_CON]-(ca)
        merge (pol)<-[:OBJ_CON]-(ua)
        merge (pol)<-[:OBJ_CON]-(comp)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status

    def test_policy2(self):
        cquery = '''
        /// Policy 2 - Admin and MLE Admin have full access to ALL Content 
        match (admin:Role {name: 'Admin'}), (mleadmin:Role {name: 'MLE Admin'})
        match (ca:content)
        match (act:fullAccess {name:"Full Access"})
        create (pol:Policy {name: 'Policy2', decision: 'Permit'})     
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:SUB_CON]-(mleadmin)
        merge (pol)<-[:OBJ_CON]-(ca)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status

    # For dev-testing AuthUser nodes, create login_user function.
    def login_user(self, email:str, password:str):
        parameters = {'email':email, 'password':password}
        cquery = '''
        MATCH (au:AuthUser {email:$email, password:$password}) <-[:owner_of]-(u:user)
        WITH count(au) AS counts
        CALL apoc.do.when(counts = 1,
            'RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {counts:counts}) YIELD value
        RETURN value.result AS result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 1:
            status = bool(True)
        else:
            status = bool(False)
        return status

if __name__ == '__main__':
    api = userAPI(url="neo4j+s://44bb2475.databases.neo4j.io", auth=("neo4j", "n04yHsQNfrl_f72g79zqMO8xVU2UvUsNJsafcZMtCFM"))

    ### For development purposes: creating sample db ###
    # Create neo4j AUTH DB roles
    api.create_role('Admin')
    api.create_role('MLE Admin')
    api.create_role('MLE User')
    api.create_role('Unapproved')

    # Create actions and public attribute
    def create_action():
        cquery = '''
        merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
        '''
        api.session.run(cquery)

    create_action()

    def create_public_attr():
        cquery = '''
        merge (p:Public:Attribute {name:'Public'})
        '''
        api.session.run(cquery)

    create_public_attr()

    # Create users and assign roles
    api.create_user('Howard', 'Yanxon', 'hg.yanxon@gmail.com', 'orcid')
    api.add_user_to_role('u_HYanxon00001','MLE Admin')
    api.create_user('Elizabeth', 'Holman', 'liz@gmail.com', 'orcid')
    api.add_user_to_role('u_EHolman00002','MLE Admin')
    api.create_user('Hari', 'Krish', 'krish@gmail.com', 'orcid')
    api.add_user_to_role('u_HKrish00003','Admin')
    api.create_user('John', 'Smith', 'smithj123@gmail.com', 'orcid')

    # Add compute location
    api.create_compute(name='Aardvark', hostname='aardvark.anl.gov', public=False, uuid='u_HKrish00003')
    api.create_compute(name='MLSandbox', hostname='mlsandbox.als.lbl.gov')
    api.create_compute(name='Vaughan', hostname='vaughan.als.lbl.gov')
    api.create_compute(name='NERSC-Perlmutter', hostname='perlmutter.nersc.gov')
    api.add_user_to_compute(uuid='u_EHolman00002', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')
    api.add_user_to_compute(uuid='u_JSmith00004', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')
    api.remove_user_from_compute(uuid='u_EHolman00002', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')

    # Add Team
    api.delete_team(name='MLExchange_Team', owner='u_EHolman00002')
    api.create_team(name='MLExchange_Team', owner='u_EHolman00002')
    api.create_team(name='random team', owner='u_HKrish00003')
    api.add_user_to_team(uuid='u_EHolman00002', tname='random team', towner='u_HKrish00003')
    api.add_user_to_team(uuid='u_HKrish00003', tname='MLExchange_Team', towner='u_EHolman00002')
    api.remove_user_from_team(uuid='u_HKrish00003', tname='MLExchange_Team', towner='u_EHolman00002')

    # Create content assets
    api.create_content_asset(name='CAsset_00001', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid')
    api.delete_content_asset(cuid='2343462')
    api.create_content_asset(name='CAsset_00001', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid')
    api.delete_content_asset(cuid='placeholdcuid')
    api.create_content_asset(name='CAsset_00002', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid', public=True)

    # Create user assets
    api.create_user_asset(name='UAsset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
    api.create_user_asset(name='UAsset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
    ### Add two policies over which to check for permission.
    api.test_policy1()
    api.test_policy2()

    ### Check for blocking of node duplication on create_user_asset.
    #['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']

    #self.archive_user(uuid='u_HKrish00003')

    #self.remove_user_content_asset(uuid='u_JSmith00004', from_master=True)
    #self.remove_user_content_asset(uuid='u_HYanxon00001', name='Asset_00001')
    
    # Check access of Smith (Unapproved) to Write to Content
    # take account of owner!!!
    SmithWriteplaceholdcuid = {"SUBJECT_NAME_UID": "u_JSmith00004","OBJECT_NAME_UID": "placeholdcuid", "ACTION_NAME":"Write"}
    cypher_query = '''
    with $SmithWriteplaceholdcuid as req
    // Stage 1 - Subject Conditions
    match (sub:Subject {name:req.SUBJECT_NAME_UID})-[:HAS_ATTR*0..5]->(sc)-[:SUB_CON]->(pol:Policy)
    with req, pol, size(collect(distinct sc)) as sat_cons
    match (pol)<-[:SUB_CON]-(rc)
    with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons

    // Stage 2 - Object Conditions
    match (obj:Object {name:req.OBJECT_NAME_UID})-[:HAS_ATTR*0..5]->(sc)-[:OBJ_CON]->(pol) 
    with req, pol, size(collect(distinct sc)) as sat_cons
    match (pol)<-[:OBJ_CON]-(rc)
    with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons

    // Stage 3 - Action Conditions
    match (act:Action {name:req.ACTION_NAME})-[:HAS_ATTR*0..5]->(sc)-[:ACT_CON]->(pol) 
    with req, pol, size(collect(distinct sc)) as sat_cons
    match (pol)<-[:ACT_CON]-(rc)
    with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons 
    return case when count(pol) = 0 or 'Deny' in collect(pol.decision) then 'Deny' else 'Permit' end as decision
    '''
    results = api.session.run(cypher_query, SmithWriteplaceholdcuid=SmithWriteplaceholdcuid).data()
    print(results)
    
    # Create placeholder auth information for testini user and testAdmin nodes.
    def create_auth_node(email:str, password:str):
        parameters = {'email':email, 'password':password}
        c_query = '''
        MATCH (u:user)-[:owner_of]->(up:UserProfile {email:$email})
        MERGE (n:AuthUser {email:$email, password:$password})<-[:owner_of]-(u)
        RETURN n
        '''
        status = api.session.run(c_query, parameters=parameters)
        return status
    
    # test login page processing with placeholder auth
    api.create_user("Test", "Initial", "testini@test.com", "orcid00001")
    api.add_user_to_role(uuid='u_TInitial00005', role="MLE User")
    api.add_user_to_team(uuid='u_TInitial00005', tname='random team', towner='u_HKrish00003')
    api.add_user_to_compute(uuid='u_TInitial00005', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')
    api.add_user_to_compute(uuid='u_TInitial00005', cname='NERSC-Perlmutter', chostname='perlmutter.nersc.gov')
    api.create_team(name='Testini Realm', owner='u_TInitial00005')
    api.create_user("Test", "Admin", "testeradmin@admin.gov", "orcid00002")
    api.add_user_to_role(uuid='u_TAdmin00006', role="Admin")
    create_auth_node(email='testini@test.com', password='mleuser')
    create_auth_node(email='testeradmin@admin.gov', password='admin')

    #test get_teams_for_user()
    api.get_teams_for_user('u_TInitial00005')
    api.get_uuid_from_email(email='hg.yanxon@gmail.com')
    api.get_members_for_team('Testini Realm', 'u_TInitial00005')

    # Close session
    api.driver.close()
