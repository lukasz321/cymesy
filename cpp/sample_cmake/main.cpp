//HW6 by Lukasz Zagaja
//SU Net ID: lzagaja SUID: 246071378

//I did not discuss with other people regarding how to solve HW6.

//CIS554 HW6. Due: 11:59pm, Saturday, Dec. 11.
//Store combinational logic circuits with one or more outputs to a database, implemented using unordered_map.
//If you finish the above, you can consider also support sequential circuits. A limited bonus will be given for this.
//In addition to submitting your code, you need to submit a PDF file ducumenting your design.
//The PDF file should contain at least 2-3 pages with single space.

#include <algorithm>
#include <iostream>
#include <fstream>
#include <cmath>
#include <map>
#include <set>
#include <unordered_map>
#include <vector>
#include <regex>

using namespace std;

auto multisetToString = [](multiset<int> m){
    string s = "";
    for (auto& i : m) s.append(to_string(i));
    return s;
};

class Circuit {
public:
    int inputs;
    int outputs;
    
    Circuit(){};
    Circuit(int num_in, int num_out) : inputs(num_in), outputs(num_out){};
    ~Circuit(){};

    /*
    NOTE: each object within "inputs" and "outputs" vector translates to a
          row in truth table.
    {
        "inputs":
            < 
                "00",
                "01",
                "10",
                "11",
            >,
        "outputs":
            <
                "0", 
                "0", 
                "0",
                "1",
            >,
    }
    */
    map<string, vector<string>> truth_table = {{"inputs", {}}, {"outputs", {}}};
    
    // multiset because it does ascending sort for us.
    // For a simple 2-in, 1-out AND gate circuit, the gate
    // signature would be < 0 1 1 3 >
    // 00 0  = 0
    // 10 0  = 1
    // 01 0  = 1
    // 11 1  = 3
    multiset<int> gate_signature = {};

    // Expected format of 'std::string row' argument is 'input output', space delimited.
    // Ex. (1) 111 10 
    //     (2) 01 1
    //     (3) 101010 121
    void addRow(string row);
};

//Circuit::Circuit(int num_in, int num_out) : inputs(num_in), outputs(num_out) {}

void Circuit::addRow(string row) {
    size_t delim_pos = row.find(" ");
    string input = row.substr(0, delim_pos);
    string output = row.substr(delim_pos + 1, row.length());
    
    truth_table["inputs"].emplace_back(input);
    truth_table["outputs"].emplace_back(output);
    
    int in_ones = 0, out_ones = 0;

    for (auto& c : input) 
        in_ones = in_ones + (int)c - 48;
    
    for (auto& c : output) 
        out_ones = out_ones + (int)c - 48;
    
    gate_signature.insert(in_ones + out_ones);
}

class myEqual {
/* 
Each unique circuit has unique signature, that is
num_inputs-num_outputs-sorted-sum_of_each_row_as_string
For example, a simple 2-in, 1-out AND gate circuit would yield 2-1-0001
*/
public:
    bool operator()(const Circuit& a, const Circuit& b) const {
        string a_signature = to_string(a.inputs) + "-" + to_string(a.inputs)\
                             + "-" + multisetToString(a.gate_signature);
        string b_signature = to_string(b.inputs) + "-" + to_string(b.inputs)\
                             + "-" + multisetToString(b.gate_signature);
        return a_signature == b_signature;
    }
};

class myHash {
/* 
Each unique circuit has unique signature, that is
num_inputs-num_outputs-sorted-sum_of_each_row_as_string
For example, a simple 2-in, 1-out AND gate circuit would yield 2-1-0001
*/

public:
    size_t operator()(const Circuit& c) const {
        string signature = to_string(c.inputs) + "-" + to_string(c.inputs)\
                           + "-" + multisetToString(c.gate_signature);
        return hash<string>()(signature);
        }
};

ostream& operator<<(ostream& str, multiset<int> M) {
    // For printing gate signatures
    str << "< ";
    for (auto& i : M) {
        str << i << " ";
    }
    str << ">";
    return str;
}

ostream& operator<<(ostream& str, Circuit& C) {
    vector<string> in = C.truth_table["inputs"];
    vector<string> out = C.truth_table["outputs"];

    str << "Inputs: " << C.inputs << endl;
    str << "Outputs: " << C.outputs << endl;

    for (int i = 0; i < in.size(); i++) {
        str << in[i] << " " << out[i] << endl;
    }

    return str;
}

ostream& operator<<(ostream& str, Circuit* C) {
    vector<string> in = C->truth_table["inputs"];
    vector<string> out = C->truth_table["outputs"];

    str << "Inputs: " << C->inputs << endl;
    str << "Outputs: " << C->outputs << endl;

    for (int i = 0; i < in.size(); i++) {
        str << in[i] << " " << out[i] << endl;
    }
    
    return str;
}

ostream& operator<<(ostream& str, unordered_map<Circuit, int, myHash, myEqual>& M) {
    /*
       Output of DB follows the same format as circuits.txt, i.e. -
       num_circuits
       num_inputs
       num_outputs
       truth_table
       num_inputs
       num_outputs
       truth_table
       ...
    */

    str << M.size() << endl;

    for (auto& i : M) {
        auto C = i.first;
        vector<string> in = C.truth_table["inputs"];
        vector<string> out = C.truth_table["outputs"];

        str << C.inputs << endl;
        str << C.outputs << endl;
        
        for (int i = 0; i < in.size(); i++) {
            str << in[i] << " " << out[i] << endl;
        }
    }
    return str;
}


int main() {
    std::ifstream file("./circuits.txt");

    unordered_map<Circuit, int, myHash, myEqual> DB;
    
    int num_circuits = -1, num_inputs = -1, num_outputs = -1;
    int num_circuits_read = 0, num_rows_read = 0;

    Circuit* circuit = nullptr;

    if (file.is_open()) {
        string line;
        while (std::getline(file, line)) {
            if (line.empty()) {
                continue;
            }
            else if (num_circuits == -1) {
                // Expected to be the very first non-empty line in circuits.txt -
                num_circuits = stoi(line);
                cout << "Expecting to read " << num_circuits << " circuits.";
                continue;
            }
            else if (num_inputs == -1) {
                // First line of every new circuit -
                num_inputs = stoi(line);
                continue;
            }
            else if (num_outputs == -1) {
                // Second line of every new circuit -
                num_outputs = stoi(line);
                circuit = new Circuit(num_inputs, num_outputs);
                continue;
            }

            // Anything that follows is a part of truth table -
            ++num_rows_read;
            circuit->addRow(line.c_str());

            if (num_rows_read == pow(2, num_inputs)) {
                // Finished reading all rows belonging this circuit -
                ++num_circuits_read;
                cout << "Read circuit " << num_circuits_read << "/" << num_circuits << "..." << endl;
                
                // Reset circuit-specific variables -
                num_inputs = num_outputs = -1;
                num_rows_read = 0;
                
                auto it = DB.find(*circuit);
                if (it == DB.end()) {
                    DB[*circuit] = rand() * rand();
                    cout << "Circuit " << num_circuits_read << " added to DB." << endl;
                }
                else {
                    cout << "The circuit is already in DB." << endl;
                }

                //cout << circuit->gate_signature << endl;
                delete circuit;
            }

            if (num_circuits_read == num_circuits) {
                cout << "All " << num_circuits << " circuits read." << endl;
                break;
            }
        }
        file.close();
    }

    cout << endl;
    cout << "Printing DB with unique circuits:" << endl;
    cout << DB << endl;

    return 0;
}
