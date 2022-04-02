import profile
from readline import get_current_history_length
from neo4j import GraphDatabase, basic_auth

class userAPI:

    def __init__(self, url, auth):
        self.url     = url
        self.auth    = auth
        self.driver  = GraphDatabase.driver(url, auth=basic_auth(self.auth[0], self.auth[1]))
        self.session = self.driver.session()
        self.role_count = {'Admin': 0, 'MLE Admin': 0, 'MLE User': 0, 'General User': 0}

        ### For developing purpose (i.e. need to delete this when is stable)
        for r in self.role_count.keys():
            status = self.delete_role(r)

        # Initiate all roles
        for r in self.role_count.keys():
            status = self.create_role(r)

        # Initiate action: full access, read, write
        self.create_action()

        ### For developing purpose
        ### Create default users for testing
        self.delete_default_users()
        self.create_default_users()

        ### For developing purpose
        ### Add compute location
        self.delete_compute_location(cluid='c_MLSandbox00001')
        self.create_compute_location(name='MLSandbox', location='Lawrence Berkeley National Laboratory')

        ### For developing purpose
        ### Add Team
        #self.delete_team(name='MLExchange_Team', owner='u_EHolman00002')
        self.create_team(name='MLExchange_Team', owner='u_EHolman00002')
        self.add_user_team(uuid='u_HKrish00003', team_name='MLExchange_Team', team_owner='u_EHolman00002')
        #self.remove_user_team(uuid='u_HKrish00003', team_name='MLExchange_Team', team_owner='u_EHolman00002')

        ### For developing purpose
        ### Add a test policy
        #self.test_policy1()
        #self.test_policy2()
        
        ### For developing purpose
        ### create_user_asset
        self.create_user_asset(name='Asset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
        ### Check for blocking of node duplication on create_user_asset.
        self.create_user_asset(name='Asset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
        #self.remove_content_asset(cuid=None, name='Asset_00001')
        
        #['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']

        #self.archive_user(uuid='u_HKrish00003')

        #self.remove_user_content_asset(uuid='u_JSmith00004', from_master=True)
        #self.remove_user_content_asset(uuid='u_HYanxon00001', name='Asset_00001')


    def test_policy1(self):
        ''' Admin have full access of profiles. '''
        cquery = '''
        /// Policy 1 - Admin has full access of profiles 
        match (admin:Role {name: 'Admin'})
        match (mp:MasterProfile {name: "MLExchange Profile"})
        match (act:Attribute {name:"Full Access"})
        create (pol:Policy {name: 'Policy1', decision: 'Permit'})
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:OBJ_CON]-(mp)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status


    def test_policy2(self):
        status = None
        return status


    def create_role(self, role):
        """ Admin Use Only. """
        parameters = {'role': role}
        cquery = '''
        MERGE (r:Role:Attribute {name:$role})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    def delete_role(self, role):
        parameters = {'role': role}
        cquery = '''
        match (r:Role {name:$role})
        detach delete r
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    def create_user(self, fname, lname, email, role='General User'):
        ''' A function to add user node. Every user is assigned as General User after sign-up. '''
        
        if role not in self.role_count:
            msg = 'The assigned role is not in the system.\nPlease add the intended role to the system.'
            raise ValueError(msg)
        cquery = '''
        match (u:user) return u
        '''
        dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
        temp_id = 'u_' + str(fname[0] + lname + str(dbindx).zfill(5))
        
        profile_name = fname+'\'s Profile'
        
        parameters = {'temp_id': temp_id, 'fname': fname, 'lname': lname, 'email': email, 'role': role, 'profile_name': profile_name}
        cquery = '''
        match (r:Role {name:$role})
        merge (up:UserProfile:Object 
        {name: $profile_name, uuid: $temp_id, fname: $fname, lname: $lname, email: $email, active:True})<-[:owner_of]-(u:Subject:user:Primitive {uuid: $temp_id})-[:has_attr]->(r)
        SET u.active = True
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    
    def assign_user_role(self, uuid, role, prev_role=None):
        ''' This method is to assign a user to a role. '''
        # If the role is already general user, do nothing
        if role == 'General User':
            return None

        # If one user is assigned to one role, then:
        # Delete relationship with the previous role
        if prev_role:
            self.delete_user_role(uuid, prev_role)

        parameters = {'uuid': uuid, 'rname': role}
        cquery = '''
        match (u:user {uuid:$uuid}), (r:Role {name:$role})
        merge (u)-[:has_attr]->(r)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_user_role(self, uuid, role):
        # This function should not need role as an argument.
        # Neo4j should know the role that is attached to the user.
        parameters = {'uuid': uuid, 'role': role}
        cquery = '''
        match (u:user {uuid: $uuid})-[rel:has_attr]->(r:Role {name:$role})
        delete rel
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    
    def archive_user(self, uuid):
        ''' Remove user from active user database and archive the uuid with its relationships to its owned assets. '''
        # How do one get the uid?
        # we are changing this to archive
        parameters = {'uuid': uuid}
        cquery = '''
        CALL {
            MATCH (p:UserProfile {uuid: $uuid})-[rel:has_attr]->()
            SET p.active = False
            RETURN rel AS rels
            UNION ALL
            MATCH (u:user {uuid: $uuid})-[rel:has_attr]->()
            SET u.active = False
            RETURN rel AS rels
        }
        
        WITH rels
        DELETE rels
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_action(self):
        cquery = '''
        merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
        '''
        status = self.session.run(cquery)
        return status

    
    def create_default_users(self):
        self.create_user('Howard', 'Yanxon', 'hg.yanxon@gmail.com', 'MLE Admin')
        self.create_user('Elizabeth', 'Holman', 'liz@gmail.com', 'MLE Admin')
        self.create_user('Hari', 'Krish', 'krish@gmail.com', 'Admin')
        self.create_user('John', 'Smith', 'smithj123@gmail.com', 'General User')


    def delete_default_users(self):
        uuids = ['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']
        for uuid in uuids:
            status = self.archive_user(uuid)
        return status

    
    def create_compute_location(self, name, location):
        """
        Create a compute location node. For admins only.
        """
        parameters = {'name': name, 'location': location}
        cquery = '''
        MATCH (cl:ComputeLoc {name:$name, location:$location})
        WITH count(cl) AS counts

        WITH counts, $name AS cl_name, $location AS cl_location
        CALL apoc.do.when(counts > 0,
            '',
            'CREATE (cl:ComputeLoc:Attribute {name:cl_name, location:cl_location, cluid:toString((cl_name)+toString(timestamp()))}) RETURN cl.cluid',
            {counts:counts, cl_name:cl_name, cl_location:cl_location}) YIELD value
        WITH value.result as cl_uid
        MATCH (cl:ComputeLoc {cluid:cl_uid})
        RETURN cl
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_compute_location(self, cluid):
        parameters = {'cluid': cluid}
        cquery = '''
        match (cl:ComputeLoc {cluid: $cluid})
        detach delete (cl)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_team(self, name:str, owner:str):
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        match (t:Team {name: $name, owner: $owner})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = False
        for s in status: is_present = s['is_present']
        
        if is_present:
            msg = 'The team name already exists.'
            raise ValueError(msg)

        cquery = '''
        match (u:user {uuid:$owner})
        merge (u)-[:owner_of]->(t:Team:Attribute:Group {name: $name, owner: $owner})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_team(self, name:str, owner:str):
        ''' Delete team. Only owner or admin access.'''
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        match (t:Team {name:$name, owner:$owner})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = False
        for s in status: is_present = s['is_present']
        
        if not is_present:
            msg = 'The team name does not exist.'
            raise ValueError(msg)

        cquery = '''
        match (t:Team {name:$name, owner:$owner})
        detach delete t
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_user_team(self, uuid:str, team_name:str, team_owner:str):
        ''' This method is to assign a user to a team. '''
        # When check if the relationship 
        # exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uuid': uuid, 'name': team_name, 'owner':team_owner}
        cquery = '''
        MATCH (u:user {uuid: $uuid}), (t:Team {name:$name, owner:$owner})
        MERGE (u)-[:has_attr]->(t)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    def remove_user_team(self, uuid:str, team_name:str, team_owner:str):
        ''' This method is to remove a user from a team. '''
        # When check if the relationship exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uuid': uuid, 'name': team_name, 'owner':team_owner}
        cquery = '''
        MATCH (u:user {uuid: $uuid})-[rel:has_attr]->(t:Team {name:$name, owner:$owner})
        DELETE rel
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    def create_user_asset(self, name:str, owner:str, type:str, path:str):
        ''' Adds a customizable user asset after checking for existance of duplicates. Transaction-locked query.'''
        parameters = {'name': name, 'owner': owner, 'path': path, 'type': type}
        cquery = '''
        MATCH (ua:UserAsset {name:$name, owner:$owner, path:$path, type:$type})
        WITH count(ua) AS counts

        WITH counts
        CALL apoc.do.when(counts = 0,
            'CREATE (ua:UserAsset:Object:Primitive {uauid: toString((name)+toString(timestamp()))}) RETURN ua.uauid AS result',
            '',
            {counts:counts, name:$name}) YIELD value

        WITH value.result as ua_uid
        MATCH (u:user {uuid: $owner}), (ua:UserAsset {uauid:ua_uid})
        CREATE (u)-[:owner_of]->(ua)
        SET ua.name = $name, ua.owner = $owner, ua.path = $path, ua.type = $type
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status
    
    def create_content_asset(self, name:str, owner:str, type:str, cuid:str, public=False):
        ''' Registers creation of new assets from content registry. Transaction-locked query.'''
        if public:
            parameters = {'name': name, 'owner': owner, 'type': type, 'cuid':cuid}
            cquery = '''
            MATCH (ca:content {cuid:$cuid})
            WITH count(ca) AS counts

            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid})
            CREATE (u)-[:owner_of]->(ca)
            SET ca.name = $name, ca.owner = $owner, ca.type = $type, ca.public = True
            RETURN ca.cuid
            '''
            status = self.session.run(cquery, parameters=parameters)
        
        else:
            parameters = {'name': name, 'owner': owner, 'type': type, 'cuid':cuid}
            cquery = '''
            MATCH (ca:content {cuid:$cuid})
            WITH count(ca) AS counts

            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid})
            CREATE (u)-[:owner_of]->(ca)<-[:has_attr]
            SET ca.name = $name, ca.owner = $owner, ca.type = $type, ca.public = False
            '''
            status = self.session.run(cquery, parameters=parameters)
        return status

    def delete_user_asset(self, uauid=None, owner=None):
        ''' Deletes user asset from graph database. Function for owner. '''
        parameters = {'owner': owner, 'uauid': uauid}
        cquery = '''
        MATCH (ua:UserAsset {owner:$owner, uauid:$uauid})
        DETACH DELETE ua
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status
    
    def delete_content_asset(self, owner:str, cuid=None):
        ''' Deletes content asset from graph database. Function for Compute API and owner. '''
        if cuid:
            parameters = {'owner':owner, 'cuid':cuid}
            cquery = '''
            MATCH (ca:content {owner:$owner, cuid:$cuid})
            DETACH DELETE ca
            '''
            status = self.session.run(cquery, parameters=parameters)
        return status

    def get_all_user_uuid(self, active=True):
        ''' Gets all information on all users (default: active), including uuids. Used for authentication and by admins. '''
        if active:
            cquery = '''
            match (up:UserProfile {active:True})
            return up
            '''
            status = self.session.run(cquery).data()
        else:
            cquery = '''
            match (up:UserProfile)
            return up
            '''
            status = self.session.run(cquery).data()
        return [s['up'] for s in status]


    def get_all_user_metadata(self):
        ''' Gets all information on all active users, excluding uuids. Front-facing User DB. '''
        cquery = '''
        match (up:UserProfile {active:True})
        return up.fname as FirstName, up.lname as LastName, up.email as Email
        '''
        status = self.session.run(cquery).data()
        return status

    
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


    def get_all_roles(self):
        cquery = '''
        match (r:Role)
        return r
        '''
        status = self.session.run(cquery).data()
        return [s['r'] for s in status]


    def get_all_computing_resources(self):
        cquery = '''
        match (cr:ComputeResource)
        return cr
        '''
        status = self.session.run(cquery).data()
        return [s['cr'] for s in status]


    def get_all_team(self):
        cquery = '''
        match (t:Team)
        return t
        '''
        status = self.session.run(cquery).data()
        return [s['t'] for s in status]


    # Make policy


if __name__ == '__main__':
    api = userAPI(url="neo4j+s://44bb2475.databases.neo4j.io", auth=("neo4j", "n04yHsQNfrl_f72g79zqMO8xVU2UvUsNJsafcZMtCFM"))
    api.driver.close()
