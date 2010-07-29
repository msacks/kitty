import javax.management.remote.JMXConnector;
import javax.management.remote.JMXConnectorFactory;
import javax.management.remote.JMXServiceURL;
import javax.management.ObjectName;
import javax.management.MBeanInfo;
import javax.management.MBeanAttributeInfo;
import javax.management.MBeanOperationInfo;
import javax.management.MBeanParameterInfo;
import java.lang.management.ManagementFactory;
import javax.management.AttributeNotFoundException;

#Python Dependencies
import sys, cmd, optparse
#from urlparse import urljoin
from cmd import Cmd

class ConnectionError :  pass 
class DomainNotFoundError : pass 
class DomainIsNoneError : pass 
class ObjectNameNotFoundError : pass 
class MBeanNotFoundError : pass 
class MBeanAttributeNotFoundError : pass 
class MBeanOperationNotFoundError : pass 

class JmxClient :

    host = None 
    port = None 
    domain = None 
    MBeansPath = None
    remote = None 
    connector = None
    
    
    def connect(self, h, p) :
        if JmxClient.remote : 
             self.disconnect()            
        try : 
            serviceURL = str()
            serviceURL = "service:jmx:rmi:///jndi/rmi://"
            serviceURL = serviceURL + h + ":" + p + "/jmxrmi"        
            try : 
                url = javax.management.remote.JMXServiceURL(serviceURL)
                JmxClient.connector = javax.management.remote.JMXConnectorFactory.connect(url)
                JmxClient.remote = self.connector.getMBeanServerConnection()           
            except :
                JmxClient.remote = None 
                JmxClient.connector = None
                raise ConnectionError 
        finally : 
            if  JmxClient.remote : 
                JmxClient.host = h
                JmxClient.port = p


    def disconnect(self) :
        try : 
            if JmxClient.remote :
                print "diconnect from " + JmxClient.host + ":" + JmxClient.port 
                try :
                    JmxClient.connector.close()
                except : 
                    pass 
        finally: 
            JmxClient.host = None 
            JmxClient.port = None 
            JmxClient.remote = None
            JmxClient.connector = None 
            JmxClient.MBeansPath = None 
            JmxClient.domaisn = None 
        
    def domains(self) : 
        if JmxClient.remote :
            domainList = [] 
            domainList = JmxClient.remote.getDomains()
            for element in domainList : 
                print element 
        else : 
            print "remote connection is None" 


    def setDomain(self, d) :
        if JmxClient.remote :
            if  d == '' : 
                    JmxClient.domain = None 
                    JmxClient.MBeansPath = None 
                    return 
            for element in JmxClient.remote.getDomains() :
                if element == d : 
                    JmxClient.domain = d 
                    JmxClient.MBeansPath = [] 
                    return 
            raise DomainNotFoundError 

                
    def ls(self) :
        if JmxClient.remote : 
            if JmxClient.domain : 
                objectName = JmxClient.domain + ":"         
                if len(JmxClient.MBeansPath) : 
                    objectName = objectName + ','.join(JmxClient.MBeansPath)
                    objectName2 = objectName + ","
                else :
                    objectName2 = objectName
                pool = javax.management.ObjectName(objectName2 + "*")
                paths = {} 
                print objectName
                print "-----"
                qNames = JmxClient.remote.queryNames(pool, None) 
                try :
                    for mbean in qNames :
                        p = mbean.toString().split(objectName2)[1].split(',')[0]
                        paths[p] = p
                    for p in paths : 
                        print  "M " + p 
                except IndexError : 
                    pass 

                try : 
                    mbean = JmxClient.remote.getMBeanInfo(javax.management.ObjectName(objectName))
                    for attr in mbean.getAttributes() :
                        try :
                            value = JmxClient.remote.getAttribute(javax.management.ObjectName(objectName), attr.getName())
                            valueStr = str(value)
                        except : 
                            valueStr = "-- " + attr.getType() + " --" 
                        if attr.isReadable() : 
                            readable = "r"
                        else :
                            readable = "-"
                        if attr.isWritable() : 
                            writable = "w" 
                        else :
                            writable = "-" 
                        print "A " + readable + writable + " " + attr.getName() + " : "  + valueStr   
                except  :
                     pass
                try :
                    mbean = JmxClient.remote.getMBeanInfo(javax.management.ObjectName(objectName))
                    for ops in mbean.getOperations() :
                        params = [] 
                        for p in ops.getSignature() : 
                            params.append(p.getType())
                        print "O " + ops.getReturnType()  + " " + ops.getName() + " ( "  + ")"
                    
                    pass
                except :
                    pass
            else :
                raise DomainIsNoneError
        

    def cd(self, path) : 
        if JmxClient.remote : 
            if JmxClient.domain : 
                if path == ".."  :
                    if len(JmxClient.MBeansPath) : 
                        JmxClient.MBeansPath.pop()
                else :
                    for p in path.split(',') :
                        JmxClient.MBeansPath.append(p)
            
        
    def get(self, att) : 
        if JmxClient.remote : 
            if JmxClient.domain : 
                objectName = JmxClient.domain + ":"         
                if len(JmxClient.MBeansPath) : 
                    objectName = objectName + ','.join(JmxClient.MBeansPath)
                try : 
                    mbean = JmxClient.remote.getMBeanInfo(javax.management.ObjectName(objectName))
                except : 
                    raise MBeanNotFoundError
                attr = None 
                for a in mbean.getAttributes() : 
                    if a.getName()  == att : 
                        attr = a 
                        break
                if not attr : 
                    raise MBeanAttributeNotFoundError                     
                try : 
                    value = JmxClient.remote.getAttribute(javax.management.ObjectName(objectName), att) 
                    valueStr = str(value)
                except :
                    valueStr = "-- " + attr.getType() + " --" 
                if attr.isReadable() : 
                    readable = "Y"
                else :
                    readable = "N"
                if attr.isWritable() : 
                    writable = "Y" 
                else :
                    writable = "N" 
                print "ObjectName :" + objectName
                print "Attribute  :" + attr.getName()
                print "Value      :"  + valueStr
                print "isReadable : " + readable 
                print "isWritable : " + writable 


    def set(self, att, val) : 
        print "set" 

    def invoke(self, rm) : 
        print "rm" 

    def pwd(self) :    
        name =  ''
        if JmxClient.domain : 
            name = JmxClient.domain + ":" + ",".join(JmxClient.MBeansPath)
        return name 

        

        
            



class JmxCmd(Cmd):
    
    jmxClient = None 
    domain = "" 
    if len(sys.argv) > 1:
        prompt = ''
    else:
        prompt = 'jmx> ' + domain 

    intro = "Simple Command-line JMX Client"


    def do_connect(self, line):
        """connect -h|--hostip <hostname or ip_addr> -p|--portnum <port>
        Establish a connection to the JMX Server. Uses jmxrmi protocol by default"""
        parser = optparse.OptionParser(conflict_handler="resolve")
        parser.add_option('-h', '--hostip', dest='host')
        parser.add_option('-p', '--portnum', dest='port')
        (options, args) = parser.parse_args(line.split())
        JmxCmd.jmxClient = JmxClient();
        try :
            JmxCmd.jmxClient.connect(options.host, options.port) 
        except ConnectionError : 
            JmxCmd.jmxClient = None 
            print "Error: failed to connect to  " + options.host + ": " + options.port  

    def do_disconnect(self, line): 
        try : 
            if JmxCmd.jmxClient : 
                JmxCmd.jmxClient.disconnect()
        finally : 
            JmxCmd.jmxClient = None 
            prompt = 'jmx>'    

    def do_domains(self, line):
        """getDomains
        Retrieve a list of all available JMX Domains"""
        if JmxCmd.jmxClient : 
            JmxCmd.jmxClient.domains()

    def do_domain(self, arg): 
        if JmxCmd.jmxClient : 
            try :
                JmxCmd.jmxClient.setDomain(arg) 
                print "set current doamin to " + arg
            except DomainNotFoundError :
                print "Error: Domain '" + arg + "' not found. "

    def do_cd(self, line) :
        try : 
            if  JmxCmd.jmxClient : 
                JmxCmd.jmxClient.cd(line)
        except ObjectNameNotFoundError : 
            print "Invalide path"
        
    def do_ls(self, line) : 
        try : 
            if JmxCmd.jmxClient : 
                JmxCmd.jmxClient.ls()
        except DomainIsNoneError : 
            print "Domain is none" 

    def do_pwd(self,line) : 
        if JmxCmd.jmxClient : 
            print JmxCmd.jmxClient.pwd()
            
    def do_get(self, line) : 
        if JmxCmd.jmxClient : 
            try : 
                JmxCmd.jmxClient.get(line)
            except MBeanAttributeNotFoundError : 
                print "Error: Attribute '" + line + "' not found." 
            except MBeanNotFoundError : 
                print "Error: MBean '" + JmxCmd.jmxClient.pwd() +  "'1 not found." 

    def do_quit(self, arg):
        if JmxCmd.jmxClient : 
            JmxCmd.jmxClient.disconnect()
        print("bye.")
        return True 
        





default_to_shell = True
if __name__ == '__main__':
    try : 
        if len(sys.argv) > 1:
            try:
                input = open(sys.argv[1], 'rt')
                sys.stdin = input
                jmxCmd = JmxCmd(input)
                jmxCmd.cmdloop()
            finally:
                input.close()
        else:
            jmxCmd = JmxCmd()
            jmxCmd.cmdloop()
    finally : 
        if jmxCmd :
            try : 
                jmxCmd.disconnect()
            except :
                pass 
