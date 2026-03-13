#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LEN 1000
#define MAX_ROWS 1000

typedef struct {
    char line[MAX_LINE_LEN];
    char normalized_ssn[10];  // 9 digits + null terminator
} CSVRow;

// Normalize SSN: remove dashes and spaces, keep only digits
void normalize_ssn(const char* ssn, char* normalized) {
    int j = 0;
    for (int i = 0; ssn[i] != '\0' && ssn[i] != ',' && j < 9; i++) {
        if (ssn[i] >= '0' && ssn[i] <= '9') {
            normalized[j++] = ssn[i];
        }
    }
    normalized[j] = '\0';
    // Pad with zeros if less than 9 digits
    while (j < 9) {
        normalized[j++] = '0';
    }
    normalized[9] = '\0';
}

// Comparison function for qsort
int comp(const void* a, const void* b) {
    CSVRow* row_a = (CSVRow*)a;
    CSVRow* row_b = (CSVRow*)b;
    return strcmp(row_a->normalized_ssn, row_b->normalized_ssn);
}

int main(int argc, char* argv[]) {
    const char* filename = (argc > 1) ? argv[1] : "myfile.csv";
    FILE* file = fopen(filename, "r");
    
    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", filename);
        return 1;
    }
    
    CSVRow rows[MAX_ROWS];
    int row_count = 0;
    char line[MAX_LINE_LEN];
    
    // Read header line
    if (fgets(line, sizeof(line), file)) {
        strncpy(rows[row_count].line, line, MAX_LINE_LEN - 1);
        rows[row_count].line[MAX_LINE_LEN - 1] = '\0';
        // Remove newline
        size_t len = strlen(rows[row_count].line);
        if (len > 0 && rows[row_count].line[len - 1] == '\n') {
            rows[row_count].line[len - 1] = '\0';
        }
        normalize_ssn(rows[row_count].line, rows[row_count].normalized_ssn);
        row_count++;
    }
    
    // Read data rows
    while (fgets(line, sizeof(line), file) && row_count < MAX_ROWS) {
        // Skip empty lines
        if (line[0] == '\n' || line[0] == '\0') {
            continue;
        }
        
        strncpy(rows[row_count].line, line, MAX_LINE_LEN - 1);
        rows[row_count].line[MAX_LINE_LEN - 1] = '\0';
        
        // Remove newline
        size_t len = strlen(rows[row_count].line);
        if (len > 0 && rows[row_count].line[len - 1] == '\n') {
            rows[row_count].line[len - 1] = '\0';
        }
        
        // Extract and normalize SSN (first field before comma)
        normalize_ssn(rows[row_count].line, rows[row_count].normalized_ssn);
        
        row_count++;
    }
    
    fclose(file);
    
    // Sort rows by normalized SSN (skip header)
    if (row_count > 1) {
        qsort(rows + 1, row_count - 1, sizeof(CSVRow), comp);
    }
    
    // Print sorted rows
    for (int i = 0; i < row_count; i++) {
        printf("%s\n", rows[i].line);
    }
    
    return 0;
}
