#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024
#define MAX_RECORDS 300

typedef struct {
    char ssn[20];
    char gender[10];
    char birthdate[20];
    char maiden_name[50];
    char last_name[50];
    char first_name[50];
    char address[100];
    char city[50];
    char state[10];
    char zip[20];
    char phone[20];
} Record;

// Normalize SSN for comparison (remove dashes and spaces)
void normalize_ssn(const char* ssn, char* normalized) {
    int j = 0;
    for (int i = 0; ssn[i] != '\0' && j < 20; i++) {
        if (ssn[i] != '-' && ssn[i] != ' ') {
            normalized[j++] = ssn[i];
        }
    }
    normalized[j] = '\0';
}

// Comparison function for qsort
int comp(const void* a, const void* b) {
    Record* rec_a = (Record*)a;
    Record* rec_b = (Record*)b;
    
    char norm_a[20], norm_b[20];
    normalize_ssn(rec_a->ssn, norm_a);
    normalize_ssn(rec_b->ssn, norm_b);
    
    return strcmp(norm_a, norm_b);
}

int main() {
    FILE* file = fopen("myfile.csv", "r");
    if (!file) {
        printf("Error: Could not open myfile.csv\n");
        return 1;
    }
    
    Record records[MAX_RECORDS];
    int count = 0;
    char line[MAX_LINE];
    
    // Skip header line
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return 1;
    }
    
    // Read records
    while (fgets(line, sizeof(line), file) != NULL && count < MAX_RECORDS) {
        char line_copy[MAX_LINE];
        strncpy(line_copy, line, sizeof(line_copy) - 1);
        line_copy[sizeof(line_copy) - 1] = '\0';
        
        // Remove newline
        char* nl = strchr(line_copy, '\n');
        if (nl) *nl = '\0';
        
        // Skip lines that are just SSNs without other data
        // Check if second field (after first comma) is empty
        char* first_comma = strchr(line_copy, ',');
        if (first_comma == NULL) continue;
        
        // Check if second field is empty (two consecutive commas or comma at end)
        if (first_comma[1] == ',' || first_comma[1] == '\0') {
            // Incomplete record, skip
            continue;
        }
        
        // Parse complete record
        char* token = strtok(line_copy, ",");
        if (token == NULL) continue;
        strncpy(records[count].ssn, token, sizeof(records[count].ssn) - 1);
        records[count].ssn[sizeof(records[count].ssn) - 1] = '\0';
        
        token = strtok(NULL, ",");
        if (token) {
            strncpy(records[count].gender, token, sizeof(records[count].gender) - 1);
            records[count].gender[sizeof(records[count].gender) - 1] = '\0';
        } else continue;
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].birthdate, token, sizeof(records[count].birthdate) - 1);
        else records[count].birthdate[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].maiden_name, token, sizeof(records[count].maiden_name) - 1);
        else records[count].maiden_name[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].last_name, token, sizeof(records[count].last_name) - 1);
        else records[count].last_name[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].first_name, token, sizeof(records[count].first_name) - 1);
        else records[count].first_name[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].address, token, sizeof(records[count].address) - 1);
        else records[count].address[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].city, token, sizeof(records[count].city) - 1);
        else records[count].city[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].state, token, sizeof(records[count].state) - 1);
        else records[count].state[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].zip, token, sizeof(records[count].zip) - 1);
        else records[count].zip[0] = '\0';
        
        token = strtok(NULL, ",");
        if (token) strncpy(records[count].phone, token, sizeof(records[count].phone) - 1);
        else records[count].phone[0] = '\0';
        
        count++;
    }
    
    fclose(file);
    
    printf("Read %d records\n", count);
    printf("\nSorting by SSN...\n\n");
    
    // Sort using qsort
    qsort(records, count, sizeof(Record), comp);
    
    // Print header
    printf("%-15s %-8s %-12s %-15s %-15s %-15s %-25s %-15s %-5s %-10s %-15s\n",
           "SSN", "Gender", "Birthdate", "Maiden Name", "Last Name", "First Name",
           "Address", "City", "State", "Zip", "Phone");
    printf("%s\n", "------------------------------------------------------------------------------------------------------------------------------------------------------------------------");
    
    // Print sorted records
    for (int i = 0; i < count; i++) {
        printf("%-15s %-8s %-12s %-15s %-15s %-15s %-25s %-15s %-5s %-10s %-15s\n",
               records[i].ssn, records[i].gender, records[i].birthdate,
               records[i].maiden_name, records[i].last_name, records[i].first_name,
               records[i].address, records[i].city, records[i].state,
               records[i].zip, records[i].phone);
    }
    
    return 0;
}
