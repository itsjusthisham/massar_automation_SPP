# -*- coding: utf-8 -*-
from library import *

if __name__ == '__main__':
    # Read the function name and form data from command line arguments
    function_name = sys.argv[1]
    
    # Execute the requested function with the provided form data
    if function_name == 'getFilesFromMassar':
        form_data = sys.argv[2]
        data = json.loads(form_data)
        response = st.getFilesFromMassar(form_data, int(data.get('session','')))
    elif function_name == 'allClasses':
        print(st.allClasses())
    elif function_name == 'getStudentsFromClasse':
        classeChoisi = sys.argv[2]
        students = st.getStudentsFromClasse(classeChoisi)
        json_data = json.dumps(students)
        sys.stdout.write(json_data)
        sys.stdout.flush()
    elif function_name == 'getAllStudents':
        classeChoisi = sys.argv[2]
        students = st.getAllStudents(classeChoisi)
        json_data = json.dumps(students)
        sys.stdout.write(json_data)
        sys.stdout.flush()
    elif function_name == 'changeNoteOfStudent':
        note = sys.argv[2]
        column = sys.argv[3]
        classe = sys.argv[4]
        st.changeNoteOfStudent(note,column,classe)
    elif function_name == 'generateRapport':
        controleNumber = sys.argv[2]
        classe = sys.argv[3]
        st.generateRapport(controleNumber, classe)
    elif function_name == 'addToMassarNotes':
        classe = sys.argv[2]
        session = sys.argv[3]
        loginInfo = sys.argv[4]
        st.addToMassarNotes(classe, session, loginInfo)
    elif function_name == 'deleteAllFiles':
        st.deleteAllFiles()