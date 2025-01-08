"""
The flamb.py script handles the iteration on a .dat file
"""

import sys
import os
from ctypes import *
import numpy as np
import re
import subprocess
from sofistik_daten import *

# Class used for the dat file mofification and information retrieval
class FileInteraction:
    def __init__(self, file_path):
        self.file_path = file_path

    def check(self, search_string):
        with open(self.file_path, 'r') as file :
            lines = file.readlines()

        for line in lines:
            if search_string in line:
                return True
        else:
            return False

    def extract_value(self, search_string):
        """
        extract the value after the input string
        """
        try:
            # Read the file content
            with open(self.file_path, 'r') as file:
                lines = file.readlines()

            # Iterate through lines to find the matching string and extract the value
            for line in lines:
                if search_string in line:
                    # Use regular expression to find the value immediately after the string
                    match = re.search(rf'{re.escape(search_string)}\s+([-+]?\d*\.?\d+)', line)
                    if match:
                        value = match.group(1)  # Extract the value found
                        print(f"Value after '{search_string}': {value}")
                        return value
                    else:
                        print(f"No value found after '{search_string}'")
                        return None

        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def modify(self, search_string, new_value):
        """
        Replace a given string with a new value
        """
        try:
            # Read the file content
            with open(self.file_path, 'r') as file:
                lines = file.readlines()

            # Flag to track if any modifications were made
            modified = False

            # Regular expression pattern to match the line
            pattern = rf'^({re.escape(search_string)}\s*)([-+]?\d*\.?\d+)(.*)$'

            # Modify the specific line
            for i, line in enumerate(lines):
                if search_string in line:
                    match = re.match(pattern, line.strip())
                    if match:
                        # Construct the new line with the updated value
                        lines[i] = f"{match.group(1)}{new_value}{match.group(3)}\n"
                        print(f"Modified line {i+1}: {lines[i].strip()}")
                        modified = True
                        break  # Exit after modifying the first matching line
                    else:
                        print(f"Line {i+1} matched search_string but not the full pattern.")
            
            if modified:
                # Write the modified content back to the file
                with open(self.file_path, 'w') as file:
                    file.writelines(lines)
                
                print(f"File '{self.file_path}' has been successfully modified.")
            else:
                print(f"No modification needed for '{search_string}'.")
        
        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def modify_coord(self, node_num, x_new, y_new, z_new):
        """
        Modifiy the node coordinates in the dat file
        """
        try:
            with open(self.file_path, 'r') as file:
                content = file.read()

            # Regular expression pattern to find the node line
            pattern = rf'^(NODE\s+{node_num}\s+X\s+)([^\s]+)(\s+Y\s+)([^\s]+)(\s+Z\s+)([^\s]+)(.*)$'
            
            # Function to replace the coordinates
            def replacement(match):
                return f"{match.group(1)}{x_new}{match.group(3)}{y_new}{match.group(5)}{z_new}{match.group(7)}"

            # Perform the substitution
            new_content, num_subs = re.subn(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)

            if num_subs > 0:
                with open(self.file_path, 'w') as file:
                    file.write(new_content)
                print(f"Modified node {node_num}: X={x_new}, Y={y_new}, Z={z_new}")
            else:
                print(f"No modification made. Node {node_num} not found.")

        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_code(self):
        """
        Add CADINP code responsible for linear calculation
        """
        code_block = """
+PROG ASE urs:9 $ Linear Analysis
HEAD Calculation of forces and moments
PAGE UNII 0
CTRL OPT WARP VAL 0
LC ALL
END
+PROG WING urs:9.1 $ Graphical Output
HEAD Graphical Output
PAGE UNII 0
CTRL EMPT YES         $ create empty pages if results not available
CTRL WARN (800 802 1) $ no warnings if no values found
CTRL WARN (804 808 1) $ no warnings if no values found
CTRL WARN 873         $ no warning for 2D visibility
#define SCHR=0.2
SCHH H6 0.2
#define FILL=-
#define FILLI=-
#define FILLC=-
#define SCHRI=-
#define SCHRC=-
SIZ2 SPLI PICT
SIZE -URS SC 0 SPLI  2x1 MARG NO FORM STAN
VIEW EG3
LC 1 DESI 1
LOAD TYPE ALL
LC 2 DESI 2
LOAD TYPE ALL
LC 3 DESI 3
LOAD TYPE ALL
LC 1 DESI 1
NODE TYPE SV SCHH YES
LC 2 DESI 2
NODE TYPE SV SCHH YES
LC 3 DESI 3
NODE TYPE SV SCHH YES
LC 1 DESI 1
DEFO TYPE FULL FAC DEFA LC CURR; STRU NUME 0 0; DEFO NO
LC 2 DESI 2
DEFO TYPE FULL FAC DEFA LC CURR; STRU NUME 0 0; DEFO NO
LC 3 DESI 3
DEFO TYPE FULL FAC DEFA LC CURR; STRU NUME 0 0; DEFO NO
LC 1 DESI 1
BEAM TYPE MY
LC 2 DESI 2
BEAM TYPE MY
LC 3 DESI 3
BEAM TYPE MY
LC 1 DESI 1
BEAM TYPE MZ
LC 2 DESI 2
BEAM TYPE MZ
LC 3 DESI 3
BEAM TYPE MZ
LC 1 DESI 1
BEAM TYPE MT
LC 2 DESI 2
BEAM TYPE MT
LC 3 DESI 3
BEAM TYPE MT
LC 1 DESI 1
BEAM TYPE VZ
LC 2 DESI 2
BEAM TYPE VZ
LC 3 DESI 3
BEAM TYPE VZ
LC 1 DESI 1
BEAM TYPE VY
LC 2 DESI 2
BEAM TYPE VY
LC 3 DESI 3
BEAM TYPE VY
LC 1 DESI 1
BEAM TYPE  N
LC 2 DESI 2
BEAM TYPE  N
LC 3 DESI 3
BEAM TYPE  N
END
"""

        try:
            # Open the file in append mode and add the code block
            with open(self.file_path, 'a') as file:
                file.write("\n")  # Ensure the block starts on a new line
                file.write(code_block)
            
            print(f"Code block added successfully to '{self.file_path}'.")

        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Script to replace 'PROG SOFILOAD' sections with new content

    def replace_sofiload(self):
        """
        replace the sofiload loading module
        """
        # New SOFILOAD content to replace with
        new_load = """
PROG SOFILOAD urs:3
HEAD EXPORT FROM DATABASE
UNIT TYPE 5
ACT  'G' GAMU 1.350000 1 PSI0 1 1 1 PART 'G' SUP PERM TITL "dead load"
ACT  'Q' GAMU 1.500000 0 PSI0 0.700000 0.500000 0.300000 PART 'Q' SUP COND TITL "variable load"
END
$ Exported by SOFILOAD     Version  17.20-70
PROG SOFILOAD urs:4
HEAD EXPORT FROM DATABASE
UNIT TYPE 5
GRP  1 VAL 'FULL' CS 9998
LC   1 'G' 1 DLX 0 -1 0 TITL "Loadcase 1"
GRP  1 VAL 'FULL' CS 9998
LC   2 'Q' 1 TITL "V"
NODE NO 1002 TYPE PG P1 0
GRP  1 VAL 'FULL' CS 9998
LC   3 'Q' 1 TITL "H"
NODE NO 1002 TYPE PX P1 0
END
"""
        with open(self.file_path, 'r') as infile:
            lines = infile.readlines()
        
        output_lines = []
        i = 0
        n = len(lines)
        sofiload_started = False
        while i < n:
            line = lines[i]
            stripped_line = line.strip()
            # Check if the line starts a 'PROG SOFILOAD' section
            if stripped_line.startswith('PROG SOFILOAD'):
                if not sofiload_started:
                    # First time we encounter 'PROG SOFILOAD'
                    sofiload_started = True
                    # Add the new SOFILOAD content
                    output_lines.append(new_load)
                # Skip lines until the next 'PROG' line or end of file
                i += 1
                while i < n and not lines[i].strip().startswith('PROG '):
                    i += 1
            else:
                if not sofiload_started:
                    # Add the current line to the output before SOFILOAD sections
                    output_lines.append(line)
                else:
                    # Skip any further 'PROG SOFILOAD' sections
                    # Continue adding lines after replacing SOFILOAD sections
                    while i < n and not lines[i].strip().startswith('PROG '):
                        i += 1
                    if i < n:
                        output_lines.append(lines[i])
                    i += 1
                    break  # Exit the loop after processing SOFILOAD sections
                i += 1
        
        # Add the remaining lines after the SOFILOAD sections
        while i < n:
            output_lines.append(lines[i])
            i += 1

        # Write the modified content to the output file
        with open(self.file_path, 'w') as outfile:
            outfile.writelines(output_lines)

# Class to interact with the sofistik database (CDB)
class CDBinteract:
    def __init__(self):
        """
        Initializes the CDB manager with the DLL library bundled with the application.
        """
        # Determine the base path
        if getattr(sys, 'frozen', False):
            # If the application is frozen, use sys._MEIPASS
            base_path = sys._MEIPASS
        else:
            # If not frozen, use the directory of the current file
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Path to the DLL in the 'DLL' folder
        dll_path = os.path.join(base_path, 'DLL', 'sof_cdb_w-2024.dll')

        # Normalize and make the DLL path absolute
        self.dll_path = os.path.abspath(os.path.normpath(dll_path))
        dll_dir = os.path.dirname(self.dll_path)

        # Always set the PATH environment variable to include the DLL directory
        os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')

        try:
            print(f"Attempting to load DLL from '{self.dll_path}'")
            print(f"Current PATH: {os.environ['PATH']}")
            self.myDLL = cdll.LoadLibrary(self.dll_path)
            print("DLL loaded successfully.")
        except Exception as e:
            print(f"Failed to load DLL '{self.dll_path}': {e}")
            raise e

        self.cdbStat = None
        self.Index = None

    def open_cdb(self, cdb_file_path, cdb_index=99):
        """
        Opens the specified CDB file.

        :param cdb_file_path: Path to the CDB file.
        :param cdb_index: CDB index (default: 99).
        """
        self.Index = c_int()
        self.Index.value = self.myDLL.sof_cdb_init(cdb_file_path.encode('utf8'), cdb_index)
        self.cdbStat = c_int()
        self.cdbStat.value = self.myDLL.sof_cdb_status(self.Index.value)
        if self.cdbStat.value != 0:
            print("CDB opened successfully, CDB Status =", self.cdbStat.value)
        else:
            print(f"Error opening CDB. Status: {self.cdbStat.value}")

    def close_cdb(self):
        """
        Closes the CDB.
        """
        self.myDLL.sof_cdb_close(0)
        self.cdbStat.value = self.myDLL.sof_cdb_status(self.Index.value)
        if self.cdbStat.value == 0:
            print("CDB closed successfully, CDB Status = 0")
        else:
            print(f"Error closing CDB. Status: {self.cdbStat.value}")

    def get_u(self):
        """
        Get the node displacement data from the CDB.
        """
        ie = c_int(0)
        RecLen = c_int(sizeof(cn_disp))
    
        nr_u = []
        ux1, ux2 = [], []
        uy1, uy2 = [], []
        uz1, uz2 = [], []
        
        while ie.value < 2:
            if ie.value >= 1:
                break
            ie.value = self.myDLL.sof_cdb_get(self.Index, 24, 2, byref(cn_disp), byref(RecLen), 1)
            nr_u.append(cn_disp.m_nr)
            ux1.append(cn_disp.m_ux)
            uy1.append(cn_disp.m_uy)
            uz1.append(cn_disp.m_uz)

            ie.value = self.myDLL.sof_cdb_get(self.Index, 24, 3, byref(cn_disp), byref(RecLen), 1)
            ux2.append(cn_disp.m_ux)
            uy2.append(cn_disp.m_uy)
            uz2.append(cn_disp.m_uz)

            RecLen = c_int(sizeof(cn_disp))
            
        ux = np.array(ux1) + np.array(ux2)
        uy = np.array(uy1) + np.array(uy2)
        uz = np.array(uz1) + np.array(uz2)
        

        if nr_u:
            max_displacement = max(ux)
            print(f"Max displacement: {max_displacement}")
            return nr_u, ux, uy, uz
        else:
            print("No displacement found.")
            return None

    def get_pos(self):
        """
        Get the node positions from the CDB.
        """
        ie = c_int(0)
        RecLen = c_int(sizeof(cnode))
        nr = []
        x = []
        y = []
        z = []
        while ie.value < 2:
            if ie.value >= 1:
                break
            ie.value = self.myDLL.sof_cdb_get(self.Index, 20, 0, byref(cnode), byref(RecLen), 1)
            nr.append(cnode.m_nr)
            x.append(cnode.m_xyz[0])
            y.append(cnode.m_xyz[1])
            z.append(cnode.m_xyz[2])

            # Always read the length of record before sof_cdb_get is called
            RecLen = c_int(sizeof(cnode))

        if nr: 
            return nr, x, y, z
        else:
            print("No positions found.")
            return None

# Class to handle calculations on the dat file
class SofiFileHandler:
    def __init__(self):
        """
        Initializes the SofiFileHandler class.
        """
        self.dat_file_path = None
        self.cdb_file_path = None
        self.sofistik_path = None

    def add_sps(self, sofistik_path):
        """
        Sets the path to the SOFiSTiK software installation.
        :param sofistik_path: Path to the SOFiSTiK software installation
        """
        self.sofistik_path = os.path.abspath(os.path.normpath(sofistik_path))

    def add_dat(self, dat_file_path):
        """
        Sets the path to the .dat file.
        :param dat_file_path: Path to the .dat file to be modified
        """
        self.dat_file_path = os.path.abspath(os.path.normpath(dat_file_path))
        print(f".dat file path set to: {self.dat_file_path}")

    def add_cdb(self, cdb_file_path):
        """
        Sets the path to the .cdb file.
        :param cdb_file_path: Path to the .cdb file
        """
        self.cdb_file_path = os.path.abspath(os.path.normpath(cdb_file_path))

    def calculate_with_sps(self):
        """
        Executes the calculation of the current .dat file using SOFiSTiK in batch mode via sps.exe.
        """
        if not self.dat_file_path:
            print("Error: .dat file path is not set. Use add_dat() to set the file path.")
            return

        if not self.sofistik_path:
            print("Error: SOFiSTiK path is not set. Use add_sps() to set the software path.")
            return

        try:
            # Construct the path to sps.exe
            sps_exe = os.path.join(self.sofistik_path, "sps.exe")
            sps_exe = os.path.abspath(sps_exe)

            if not os.path.isfile(sps_exe):
                print(f"Error: sps.exe not found at {sps_exe}.")
                return

            # Command to run sps.exe with the specified .dat file
            sps_command = [sps_exe, self.dat_file_path]

            # Launch sps.exe with the .dat file and wait for it to complete
            process = subprocess.Popen(
                sps_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Wait for the process to complete
            stdout, stderr = process.communicate()

            # Check if the process finished successfully
            if process.returncode == 0:
                print("Calculation successfully completed in SOFiSTiK.")
            else:
                print(f"Calculation failed with exit code {process.returncode}.")
                print(stderr.decode())

        except Exception as e:
            print(f"Error during SOFiSTiK execution: {e}")

# Class defining initialisation and loop functions to iterate on the dat file
class Iteration:
    def __init__(self, V, H, epsilon, cdb_file_path, dat_file, sofistik_path):
        self.epsilon = epsilon
        self.cdb_file_path = cdb_file_path 
        self.dat_file = dat_file
        self.sofistik_path = sofistik_path
        self.nr = None
        self.x = None
        self.y = None
        self.z = None
        self.nr_u = None
        self.ux = None
        self.uy = None
        self.uz = None
        self.V = V
        self.H = H

    def initialize(self):
        """
        Initilisation of the process: 
        Modifying the dat to make it iterable by changing load and adding the ASE module
        Retrieving initial data
        Launching first calculation
        """
        # load dat, replace sofiload, and add linear analysis to DAT file
        DAT_interaction = FileInteraction(self.dat_file)
        DAT_interaction.replace_sofiload()
        if not DAT_interaction.check('+PROG ASE'):
            DAT_interaction.add_code()
            
        # Modify load values
        DAT_interaction.modify('NODE NO 1002 TYPE PG P1', str(self.V))
        DAT_interaction.modify('NODE NO 1002 TYPE PX P1', str(self.H))
        
        CDBstatus = CDBinteract()
        CDBstatus.open_cdb(self.cdb_file_path)
        self.nr, self.x, self.y, self.z = CDBstatus.get_pos()
        S = [0] * len(self.nr)
        self.nr_u, self.ux, self.uy, self.uz = S, S, S, S
        CDBstatus.close_cdb()

        # Compute a first time the displacement
        first_iteration = SofiFileHandler()
        first_iteration.add_sps(self.sofistik_path)  # Setting the SOFiSTiK path
        first_iteration.add_cdb(self.cdb_file_path)
        first_iteration.add_dat(self.dat_file)
        first_iteration.calculate_with_sps()
        
    def loop(self):
        """
        Looping function updating position and computing displacement
        Stops under epsilon threshold
        """
        delta_ux = self.epsilon + 1        
        DAT_interaction = FileInteraction(self.dat_file)

        while delta_ux > self.epsilon:
            print("delta_ux :", delta_ux)
            ux_prev = self.ux.copy()

            # Open cdb and get data after sps.exe has finished
            CDBstatus = CDBinteract()
            CDBstatus.open_cdb(self.cdb_file_path)
            self.nr_u, self.ux, self.uy, self.uz = CDBstatus.get_u()
            print(len(self.nr), self.nr)
            print(len(self.nr_u), self.nr_u)
            print(len(self.ux), self.ux)
            CDBstatus.close_cdb()

            # Process positions and displacements
            unique_positions = {}
            for nr, x, y, z in zip(self.nr, self.x, self.y, self.z):
                if nr != 0:
                    unique_positions[nr] = (x, y, z)

            unique_displacements = {}
            for nr_u, ux, uy, uz in zip(self.nr_u, self.ux, self.uy, self.uz):
                if nr_u != 0:
                    if nr_u in unique_displacements:
                        dux_prev, duy_prev, duz_prev = unique_displacements[nr_u]
                        unique_displacements[nr_u] = (dux_prev + ux, duy_prev + uy, duz_prev + uz)
                    else:
                        unique_displacements[nr_u] = (ux, uy, uz)

            # Update node coordinates
            for node in unique_positions:
                x, y, z = unique_positions[node]
                dux, duy, duz = unique_displacements.get(node, (0.0, 0.0, 0.0))

                new_x = str(x + dux)
                new_y = str(y + duy)
                new_z = str(z + duz)

                DAT_interaction.modify_coord(str(node), new_x, new_y, new_z)

            # Perform calculations with the new displacement
            iterate = SofiFileHandler()
            iterate.add_sps(self.sofistik_path)  # Setting the SOFiSTiK path here as well
            iterate.add_cdb(self.cdb_file_path)
            iterate.add_dat(self.dat_file)
            iterate.calculate_with_sps()

            # Calculate the new delta_u (difference between the old and new ux values)
            delta_ux = abs(max(self.ux) - max(ux_prev))
            print(max(self.ux))
            print(delta_ux)

            # Check for convergence
            if delta_ux < self.epsilon:
                print("Convergence achieved.")
                break