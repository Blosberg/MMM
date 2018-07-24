/*
 AUTHOR : BRENDAN OSBERG: Begun July 2016  
 You are free to copy and redistribute this script, provided you cite and give credit 

 This script makes projections for proportional seating arrangements for the MMM model,
 based on raw FPP input.

*/

// Include various dependencies 
#include <stdlib.h>
#include <fstream>
#include <cmath>
#include <iostream>
#include <stdio.h>
#include <queue>

using namespace std;


// --- Define class object "quotient"  (Q objects described in paper)

class quotient{   
  public:
  quotient();
  double  value;     // generally, # of votes divided by jval (below)
  int     jval;      // array of values: 1,2,3,... etc. 
  bool    assigned;  // has this quotient been attributed to a seat yet?
  string party_att;  // Three character string denoting party
  };

quotient::quotient()
  {
  value     = 0.0;
  jval      = 0;
  assigned  = false;
  party_att ='\0';
  }
//----------------------------------------------


// --- Define class object "party" 
class party{

  public:
  party();
  string name;
  int votes;
  double vote_share;
  int seats_initial;  // # seats assigned directly from constituencies
  int seats_assigned; // # seats currently assigned at a given moment 
                      // within this algorithm.

  bool most_over_represented;
  double * party_quotient_list;
  };

party::party()
  {
  name                  = '\0';
  votes                 = 0;
  seats_initial         = seats_assigned = 0; 
  vote_share            = 0.0;
  most_over_represented = false;
  }


bool should_terminate ( const  quotient * Total_quotient_list, party * all_parties, const int qi, const int Seats_total_init, int & total_seats_assigned, const int Seats_max_cutoff, const int Num_parties, const int total_votes, const bool count_NotA );


double seats_overrepresented (const int seats_assigned, const int total_seats_assigned, const int votes, const int total_votes );


// --- Begin main *******************************************************

int main(int argc, char *argv[])
{

// Declare and initialize variables 
string FILE_in;   // input file path taken as command-line argument
string FILE_out;  // output path (derived from above)
string FILE_qout; // output path for the list of quotients

ifstream datin;
ofstream datout;

int Seats_total_init=0;
int Seats_max_cutoff;

int total_votes=0;
int i=0, j=0;
bool count_NotA;

if ( argc != 3 )
  {
  cout << "\n ERROR: program requires 2 input arguments; the name of the input file and the boolean count_NotA. ";
  cout << " please supply these command line parameters at runtime.\n";
  exit(1);
  }


FILE_in  = argv[1];
FILE_in.append(".in");

count_NotA = atoi(argv[2]);
FILE_out   = argv[1];


if (count_NotA )
  {
  FILE_out.append("_NotA_counted");
  }
FILE_out.append(".out");


// occasional cross-checking.
// 
// cout << "\n command line parameters are: " << endl;
// cout <<  FILE_in    << endl;
// cout <<  FILE_out   << endl;
// cout <<  count_NotA << endl;
// exit(0);
// 

// --- Populate party list and read in member data from input file:

int Num_parties=6;    // "Other" is treated as a party (although awarded no seats)
party all_parties[Num_parties];

datin.open(FILE_in.c_str());
datout.open(FILE_out.c_str());


if( datin.fail() )
  {
  cout << "\n ERROR, can't find input file. exiting \n";
  exit(1);
  }
else
  {//----succeeded reading in file
  for(i=0;i<Num_parties;i++)
    {
    datin >>  all_parties[i].name; 
    datin >>  all_parties[i].seats_initial;  
    datin >>  all_parties[i].votes;

    all_parties[i].seats_assigned = 0;

    Seats_total_init += all_parties[i].seats_initial;
    total_votes      += all_parties[i].votes;
    }

  }
Seats_max_cutoff = 2*Seats_total_init;
 
// --- populate each party's list of quotients 
quotient Total_quotient_list[Num_parties*2*Seats_total_init];

for(i=0;i<Num_parties;i++)
  {
  all_parties[i].vote_share          = double(all_parties[i].votes)/double(total_votes); 
  all_parties[i].party_quotient_list = new double[2*Seats_total_init];
  
  for(j=0;j<2*Seats_total_init;j++)
    {
    all_parties[i].party_quotient_list[j] = double(all_parties[i].votes)/(double(j+1));

    //   location:  -->|_______________________|<--  is just to assign a slot in memory. 
    Total_quotient_list[i*(2*Seats_total_init)+j].party_att = all_parties[i].name;
    Total_quotient_list[i*(2*Seats_total_init)+j].jval      = j;
    Total_quotient_list[i*(2*Seats_total_init)+j].value     = double(all_parties[i].votes)/(double(j+1));

    if ( j >= all_parties[i].seats_initial )
       {
       Total_quotient_list[i*(2*Seats_total_init)+j].assigned  = false;
       }
    else if ( j < all_parties[i].seats_initial )
       {
       Total_quotient_list[i*(2*Seats_total_init)+j].assigned  = true;
       }

    }
    //----- the j'th entry is now the party's votes divided by j+1;
  }
// each party's quotient list is now sorted individually, and the first "C" seats are
// "assigned", where C is the # of seats the party already won from Constituency races. 
// Total_quotient_list is stored as a block by party; below we will sort that (first
// by "assigned" status, and then by quotient value


// --- CHECK WHICH PARTY is the most OVER-REPRESENTED. --------------

int    most_OR_index=0;  // index of the Most over-represented party
double most_OR=0.0;
double current_rdiff;

for(i=0;i<Num_parties;i++)
  {
  current_rdiff  =  double(all_parties[i].seats_initial)/double(Seats_total_init) - (double(all_parties[i].votes/double(total_votes)) );

  if( current_rdiff > most_OR ) 
    {
    most_OR       = current_rdiff;
    most_OR_index = i;
    }
  }

all_parties[most_OR_index].most_over_represented=true;

// --- SORT the quotients list ----------

int array_size = Num_parties*2*Seats_total_init; // array of quotients to be ranked.

quotient temp1;
quotient temp2;


// --- first sort by "assigned" to bring the 308 constituency seats to the front of the list
for (i=0; i<array_size; i++)
  {
  for (j=i+1; j<array_size; j++)
    {
    if( Total_quotient_list[j].assigned && !Total_quotient_list[i].assigned   )
      {
      temp1                   = Total_quotient_list[i];
      Total_quotient_list[i]  = Total_quotient_list[j];
      Total_quotient_list[j]  = temp1;
      }
    }
  }

// --- then sort the first 308 quotients by value (not actually necessary, but done for tidiness and visualization)
for (i=0; i<Seats_total_init; i++)
  {
  for (j=i+1; j<Seats_total_init; j++)
    {
    if(  Total_quotient_list[j].value > Total_quotient_list[i].value  )
      {
      temp1                   = Total_quotient_list[i];
      Total_quotient_list[i]  = Total_quotient_list[j];
      Total_quotient_list[j]  = temp1;
      }
    }
  }

// --- then sort the remaining quotients (this *IS* necessary)
for (i=Seats_total_init; i<array_size; i++)
  {
  for (j=i+1; j<array_size; j++)
    {
    if( ( Total_quotient_list[j].value > Total_quotient_list[i].value ) || ( Total_quotient_list[j].assigned && !Total_quotient_list[i].assigned )  )
      {
      temp1                   = Total_quotient_list[i];
      Total_quotient_list[i]  = Total_quotient_list[j];
      Total_quotient_list[j]  = temp1;
      }
    }
  }

ofstream  qout;

FILE_qout   = argv[1];
FILE_qout.append("_qlist");
if (count_NotA )
  {
  FILE_qout.append("_NotA_counted");
  }
FILE_qout.append(".out"); 
qout.open(FILE_qout.c_str());

for( i=0; i < Seats_max_cutoff; i++ )
{
qout << Total_quotient_list[i].jval      << "\t";
qout << Total_quotient_list[i].value     << "\t";  // generally, # of votes divided by jval (below)
qout << Total_quotient_list[i].assigned  << "\t";  // has this quotient been attributed to a seat yet?
qout << Total_quotient_list[i].party_att << endl;  // Three character string denoting party
}
qout.close();


// ----------- double-check that the quotient list looks right:
// datout << "\n Checking the quotient list:\n";
// 
// for (i=0; i<array_size; i++)
//   {
//   datout << Total_quotient_list[i].value    << "\t"; 
//   datout << Total_quotient_list[i].jval     << "\t"; 
//   datout << Total_quotient_list[i].assigned << "\t"; 
//   datout << Total_quotient_list[i].party_att << endl; 
//   } 
// exit(0);


// Total_quotient_list IS NOW ORDERED first by "assigned" status, and then by "value" 
// it has size "array_size". 
// only the first 308 quotients are "assigned"

//  NOW ASSIGN SEATS IN ORDER 
int total_seats_assigned  = 0; 
bool allocated;

for (i=0; i<array_size; i++)
  {

  if ( should_terminate( Total_quotient_list, all_parties, i, Seats_total_init, total_seats_assigned, Seats_max_cutoff,  Num_parties, total_votes, count_NotA ) )     
     {
     break;
     } 
  allocated = false;

  for(  j=0;j<Num_parties;j++)
    {
    if( Total_quotient_list[i].party_att == all_parties[j].name)
      {

      allocated = true;
      if( Total_quotient_list[i].party_att != "Oth")
        { //---- party 'other' doesn't get seats, obviously.
        all_parties[j].seats_assigned++;
        total_seats_assigned++;  
        }//--finished assigning to seat to party (provided it wasn't "Oth")
      }//--finished "if divisor list name matches"    
    }//--- finished scanning through the parties

  if( !allocated )
    {
    cout << "\n ERROR: failed to assign seat to party " << Total_quotient_list[i].party_att << " Exiting ";
    exit(1);
    }

  Total_quotient_list[i].assigned = true;
  }//---finished scanning through the array of quotients (we should never get this far.)

finished_allocation:

// OUTPUT TO FILE 

for(i=0;i<Num_parties;i++)
  {
  datout <<  all_parties[i].name          << " \t "; 
  datout <<  all_parties[i].seats_initial << " \t ";  
  datout <<  all_parties[i].votes         << " \t ";
  datout <<  all_parties[i].vote_share    << " \t ";
  datout <<  all_parties[i].seats_assigned   << " \t ";
  datout <<  (double(all_parties[i].seats_assigned) / double(total_seats_assigned)) << endl;
  }

// CLEAN UP MEMORY 
for(i=0;i<Num_parties;i++)
  {
  delete [] all_parties[i].party_quotient_list;
  }

// OUTPUT message to screen and terminate
cout << "\n ========================================= \n program complete.\n";
cout << " final number of seats assigned: " << total_seats_assigned << " , majority threshold=" << double(total_seats_assigned)/2.0
<< endl;

return 0;
} // End of main()


// =================   DEFINE FUNCTIONS   ===============

bool should_terminate ( const quotient * Total_quotient_list, party * all_parties, const int qi, const int Seats_total_init, int & total_seats_assigned, const int Seats_max_cutoff, const int Num_parties, const int total_votes, const bool count_NotA )
{
int i=0, j=0;
int total_seats_xcheck = 0;
bool underrep_found=false;
bool result = false;

// --- check if we've allocated all Const. seats yet. If not, keep going.
if ( qi < Seats_total_init )
  { 
    return(false); 
  }

// --- x-check total number of seats, and get the next candidate party
bool next_found=false;
int  next_index=-1; 
for(j=0;j<Num_parties;j++)
  {
  total_seats_xcheck  += all_parties[j].seats_assigned;
  if  ( all_parties[j].name ==  Total_quotient_list[qi].party_att )
    {
    if ( next_found )
       {
       cout << "\n ERROR: ambiguous party name attached ";
       cout << " to next candidate in should_terminate. Exiting.";
       exit(1);
       }
    next_found = true; // should only happen once
    next_index = j; 
    }
  }

if (  total_seats_xcheck != total_seats_assigned || !next_found )//sanity check.
  {
  cout << "\n ERROR: in should_terminate function.\n";
  cout << " inconsistent total seat count, or next allocation not found. \n "; 
  cout << " total_seats_xcheck   = " << total_seats_xcheck   << endl;
  cout << " total_seats_assigned = " << total_seats_assigned << endl;
  exit(1);
  }

if ( total_seats_assigned >= Seats_max_cutoff )// If we've reached cutoff, then terminate
    {
    cout << "\n Parliament size reached cutoff threshold. Terminating at seat #";
    cout << total_seats_assigned;
    cout << " last seat assigned to the " << all_parties[j].name << " party.\n";
    return ( true ); 
    }

// ------------- 

if ( count_NotA ) // counting "None of the Above" means each party's share  
  { // exit if no party remains under-represented by more than an integer 

  underrep_found = false;
    for(j=0;j<(Num_parties-1);j++)
      { //                ^ -1 because we don't care if party "Other" is underrepresented 

      if ( seats_overrepresented (all_parties[j].seats_assigned, total_seats_assigned, all_parties[j].votes, total_votes ) < -1  )
         { // in this case, under-representation of a party exceeds a full integer 
           // (meaning this party has the right to claim another full seat)  
           // therefore,  do not terminate seat allocation process yet. 
         underrep_found = true;
         break; 
         }
      } 

  if ( underrep_found )
     { result = false; }
  else
     { result = true;  }
  }
else
  { //not counting NotA: fraction of votes *among major parties* -> fraction of seats
    // exit if the most overrepresented party has just been awarded a seat:

    result = false;

   
 // check each party for underrepresentation 
     
  if( all_parties[next_index].seats_assigned > all_parties[next_index].seats_initial && all_parties[next_index].most_over_represented)
    {
  
    result = true;

    all_parties[next_index].seats_assigned++;
    total_seats_assigned++;  

    }
  
  }  

return result;
}

//-------------------------------
double seats_overrepresented (const int seats_assigned, const int total_seats_assigned, const int votes, const int total_votes )
{
double result;

result = double(seats_assigned) -  double(total_seats_assigned)*(double(votes)/double(total_votes) ) ;

return result;
}
