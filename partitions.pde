int[] convertIntegers(ArrayList<Integer> integers)
{
    int[] ret = new int[integers.size()];
    for (int i=0; i < ret.length; i++)
    {
        ret[i] = integers.get(i).intValue();
    }
    return ret;
}

int[] printArray(int p[], int n) 
{ 
    ArrayList<Integer> j = new ArrayList<Integer>();
    for (int i = 0; i < n; i++) {
        //System.out.print(p[i]+" "); 
        j.add(p[i]);
    }

    return convertIntegers(j);
} 
  
// Function to generate all unique partitions of an integer 
ArrayList<int[]> printAllUniqueParts(int n) 
{ 
    ArrayList<int[]> i = new ArrayList<int[]>();
    int[] p = new int[n]; // An array to store a partition 
    int k = 0;  // Index of last element in a partition 
    p[k] = n;  // Initialize first partition as number itself 
    
    while (true) 
    { 
        // print current partition 
        i.add(printArray(p, k+1)); 
        //i.add(p);
 
        // Generate next partition 
 
        // Find the rightmost non-one value in p[]. Also, update the 
        // rem_val so that we know how much value can be accommodated 
        int rem_val = 0; 
        while (k >= 0 && p[k] == 1) 
        { 
            rem_val += p[k]; 
            k--; 
        } 
 
        // if k < 0, all the values are 1 so there are no more partitions 
        if (k < 0)  return i; 
 
        // Decrease the p[k] found above and adjust the rem_val 
        p[k]--; 
        rem_val++; 
 
 
        // If rem_val is more, then the sorted order is violated.  Divide 
        // rem_val in different values of size p[k] and copy these values at 
        // different positions after p[k] 
        while (rem_val > p[k]) 
        { 
            p[k+1] = p[k]; 
            rem_val = rem_val - p[k]; 
            k++; 
        } 
 
        // Copy rem_val to next position and increment position 
        p[k+1] = rem_val; 
        k++; 
    } 
} 

ArrayList<int[]> getAllUniqueParts(int n) {
    ArrayList<int[]> i = printAllUniqueParts(n);
    ArrayList<int[]> j = new ArrayList<int[]>();
    
    int no_larger;
    for (int k = 0; k < i.size(); k++) {
        if (i.get(k) != null && i.get(k).length >= 15) {
            no_larger = 1;
            for (Integer a : i.get(k)) {
                if (a > 3) no_larger = 0;
            }
            if (no_larger == 1) j.add(i.get(k));
        }
    }
    return j;
}
