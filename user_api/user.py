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
        
        ### For developing purpose. Delete MLExchange_Profile
        self.delete_mlex_profile()
        self.delete_mlex_asset()

        # Create MLExchange Profile and MLExchange Asset
        self.create_mlex_profile()
        self.create_mlex_asset()

        # Initiate action: full access, read, write
        self.create_action()

        ### For developing purpose
        ### Create default users for testing
        self.delete_default_users()
        self.add_default_users()

        ### For developing purpose
        ### Add compute location
        self.delete_compute_resource(cuid='c_MLSandbox00001')
        self.add_compute_resource(name='MLSandbox', location='Lawrence Berkeley National Laboratory', profile=None)

        ### For developing purpose
        ### Add Team
        #self.remove_team('MLExchange_Team')
        self.add_team('MLExchange_Team')
        self.assign_user_team(uuid='u_HKrish00003', team_name='MLExchange_Team')
        #self.remove_user_team(uuid='u_HKrish00003', team_name='MLExchange_Team')

        ### For developing purpose
        ### Add a test policy
        #self.test_policy1()
        #self.test_policy2()
        
        ### For developing purpose
        ### add_user_asset
        self.add_user_asset(name='Asset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
        ### Check for blocking of node duplication on add_user_asset.
        self.add_user_asset(name='Asset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
        #self.remove_content_asset(cuid=None, name='Asset_00001')
        
        #['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']
        self.add_user_to_content_asset(uuid='u_JSmith00004', cuid=None, name=None, to_master=True)
        self.add_user_to_content_asset(uuid='u_HYanxon00001', name='Asset_00001', to_master=False)

        print(self.get_all_user_uuid())
        print(self.get_all_assets())

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
        parameters = {'role': role}
        cquery = '''
        create (r:Role:Attribute {name:$role})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_role(self, role):
        if role not in self.role_count:
            self.role_count[role] = 0
        status = self.create_role(role)
        return status


    def delete_role(self, role):
        parameters = {'role': role}
        cquery = '''
        match (r:Role {name:$role})
        detach delete r
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status
       

    def add_user(self, fname, lname, email, role='General User'):
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
        match (ap:MlexProfile {name: "MLExchange Profile"})
        merge (n:Subject:user:Primitive {uuid: $temp_id})-[:has_attr]->(r)
        // Create user's profile
        merge (n)-[:owner_of]->(p:UserProfile:Object 
        {name: $profile_name, uuid: $temp_id, fname: $fname, lname: $lname, email: $email})-[:has_attr]->(ap)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    
    def create_mlex_profile(self, name='MLExchange Profile'):
        parameters = {'name': name}
        cquery = '''
        create (ap:MlexProfile:Attribute {name: $name})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_mlex_profile(self, name='MLExchange Profile'):
        parameters = {'name': name}
        cquery = '''
        match (ap:MlexProfile {name: $name})
        detach delete ap
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_user_profile(self):
        # I'm thinking that user node should only contains uuid.
        # Meanwhile, we can create another node for the user that contains his/her profile. This node is called profile node.
        # Profile will include, but not limited to, first name, last name, email, institution, etc.
        # I wonder if we need so make this separate from add_user because currently this function is included in add_user
        status = None
        return status

    
    def assign_user_role(self, uuid, role, prev_role=None):
        ''' This method is to assign a user to a role. '''
        # If the role is already general-user, do nothing
        if role == 'General-User':
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

    
    def delete_user(self, uuid):
        # How do one get the uid?
        # we are changing this to archive
        parameters = {'uuid': uuid}
        cquery = '''
        match (u:user {uuid: $uuid})
        match (p:UserProfile {uuid: $uuid})
        detach delete (u)
        detach delete (p)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_action(self):
        cquery = '''
        merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
        '''
        status = self.session.run(cquery)
        return status

    
    def add_default_users(self):
        self.add_user('Howard', 'Yanxon', 'hg.yanxon@gmail.com', 'MLE Admin')
        self.add_user('Elizabeth', 'Holman', 'liz@gmail.com', 'MLE Admin')
        self.add_user('Hari', 'Krish', 'krish@gmail.com', 'Admin')
        self.add_user('John', 'Smith', 'smithj123@gmail.com', 'General User')


    def delete_default_users(self):
        uuids = ['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']
        for uuid in uuids:
            status = self.delete_user(uuid)
        return status

    
    def add_compute_resource(self, name, location, profile=None):
        """
        We need to work on the profile argument. Essentially, profile contain ngpu, ncpu, etc. Then,
        we need to pass this information to the computing resource profile.
        """
        cquery = '''
        match (cr:ComputeResource) return cr
        '''
        dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
        cuid = 'c_' + name + str(dbindx).zfill(5)
        profile_name = name + '\'s Profile'

        parameters = {'name': name, 'location': location, 'cuid': cuid, 'profile_name': profile_name, 'profile': 'None'}
        cquery = '''
        match (ap:MasterProfile {name: "MLExchange Profile"})
        create (cr:ComputeResource:Object:Primitive {name: $name, cuid: $cuid})
        merge (cr)-[:owner_of]->(cp:ComputeResourceProfile:Object {cuid: $cuid, profile_name: $profile_name, location: $location, profile: $profile})-[:has_attr]->(ap)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_compute_resource(self, cuid):
        parameters = {'cuid': cuid}
        cquery = '''
        match (c:ComputeResource {cuid: $cuid})
        match (cp:ComputeResourceProfile {cuid: $cuid})
        detach delete (c)
        detach delete (cp)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_team(self, name):
        cquery = '''
        match (t:Team {name: $name})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters={'name': name})
        is_present = False
        for s in status: is_present = s['is_present']
        
        if is_present:
            msg = 'The team name is already existed.'
            raise ValueError(msg)

        cquery = '''
        create (t:Team:Attribute {name: $name})
        '''
        status = self.session.run(cquery, parameters={'name': name})
        return status


    def remove_team(self, name):
        cquery = '''
        match (t:Team {name: $name})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters={'name': name})
        is_present = False
        for s in status: is_present = s['is_present']
        
        if not is_present:
            msg = 'The team name doesn\'t exist.'
            raise ValueError(msg)

        cquery = '''
        match (t:Team {name: $name})
        detach delete t
        '''
        status = self.session.run(cquery, parameters={'name': name})
        return status


    def assign_user_team(self, uuid, team_name):
        ''' This method is to assign a user to a team. '''
        # When check if the relationship exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uuid': uuid, 'name': team_name}
        cquery = '''
        match (u:user {uuid: $uuid}), (t:Team {name: $name})
        return exists((u)-[:has_attr]-(t)) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = status.single()[0]
        #print(is_present)

        if not is_present:
            cquery = '''
            match (u:user {uuid: $uuid})
            match (t:Team {name: $name})
            merge (u)-[:has_attr]->(t)
            '''
            status = self.session.run(cquery, parameters=parameters)
        return status


    def remove_user_team(self, uuid, team_name):
        ''' This method is to remove a user from a team. '''
        # When check if the relationship exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uuid': uuid, 'name': team_name}
        cquery = '''
        match (u:user {uuid: $uuid}), (t:Team {name: $name})
        return exists((u)-[:has_attr]-(t)) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = status.single()[0]
        #print(is_present)

        parameters = {'uuid': uuid, 'name': team_name}
        cquery = '''
        match (u:user {uuid: $uuid})-[r:has_attr]->(t:Team {name: $name})
        delete r
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_mlex_asset(self, name='MLExchange Asset'):
        parameters = {'name': name}
        cquery = '''
        create (ma:MlexAsset:Attribute {name: $name})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_mlex_asset(self, name='MLExchange Asset'):
        parameters = {'name': name}
        cquery = '''
        match (ma:MlexAsset {name: $name})
        detach delete ma
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_user_asset(self, name:str, owner:str, type:str, path:str):
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

    def remove_content_asset(self, cuid=None, name=None):
        parameters = {'name': name, 'cuid': cuid}
        if cuid:
            cquery = '''
            match (ca:content {cuid: $cuid})
            detach delete ca
            '''
        else:
            cquery = '''
            match (ca:content{name: $name})
            detach delete ca
            '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_user_to_content_asset(self, uuid, cuid=None, name=None, to_master=False):
        ''' Add a user to access a content registry asset. '''
        if to_master:
            parameters = {'name': 'MLExchange Asset', 'uuid': uuid}
            cquery = '''
            match (ma:MasterAsset {name: $name})
            match (u:user {uuid: $uuid})
            merge (u)-[:has_attr]->(ma)
            '''
            status = self.session.run(cquery, parameters=parameters)
        
        else:
            parameters = {'name': name, 'cuid': cuid, 'uuid': uuid}
            if cuid:
                cquery = '''
                match (ca:content {cuid: $cuid})
                match (u:user {uuid: $uuid})
                merge (u)-[:has_attr]->(ass)
                '''
            else:
                cquery = '''
                match (ass:Asset {name: $name})
                match (u:user {uuid: $uuid})
                merge (u)-[:has_attr]->(ass)
                '''
            status = self.session.run(cquery, parameters=parameters)

        return status


    def remove_user_from_content_asset(self, uuid, cuid=None, name=None, from_master=False):
        if from_master:
            parameters = {'name': 'MLExchange Asset', 'uuid': uuid}
            cquery = '''
            match (u:user {uuid: $uuid})-[rel:has_attr]->(ma:MasterAsset {name: $name})
            delete rel
            '''
            status = self.session.run(cquery, parameters=parameters)

        else:
            parameters = {'name': name, 'cuid': cuid, 'uuid': uuid}
            if cuid:
                cquery = '''
                match (u:user {uuid: $uuid})-[rel:has_attr]->(ass:Asset {cuid: $cuid})
                delete rel
                '''
            else:
                cquery = '''
                match (u:user {uuid: $uuid})-[rel:has_attr]->(ass:Asset {name: $name})
                delete rel
                '''
            status = self.session.run(cquery, parameters=parameters)

        return status


    def get_all_user_uuid(self):
        ''' Gets all information on all users, including uuids. Used for authentication and by admins. '''
        cquery = '''
        match (up:UserProfile)
        return up.fname as FirstName, up.lname as LastName, up.email as Email, up.uuid as UUID
        '''
        status = self.session.run(cquery).data()
        return status #[s['u'] for s in status]


    def get_all_user_metadata(self):
        ''' Gets all information on all users, excluding uuids. Front-facing User DB. '''
        cquery = '''
        match (up:UserProfile {uuid:$uuid})
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
        return status


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
