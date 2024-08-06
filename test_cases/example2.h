#ifndef EXAMPLE_STRUCTS_H
#define EXAMPLE_STRUCTS_H

// Example struct definitions
typedef struct {
    unsigned int field1 : 4;  // 4 bits
    unsigned int field2 : 8;  // 8 bits
    unsigned int field3 : 3;  // 3 bits
    unsigned int field4 : 1;  // 1 bit (can be used as a boolean)
    int field5;  // 16 bits
} ExampleStruct1;

typedef struct {
    unsigned int status : 2;  // 2 bits for status (e.g., 0-3)
    unsigned int errorCode : 6;  // 6 bits for error codes
    unsigned int retryCount : 4;  // 4 bits for retry count
} ExampleStruct2;

typedef struct {
    unsigned int mode : 3;  // 3 bits for mode selection
    unsigned int priority : 5;  // 5 bits for priority levels
    unsigned int flags : 8;  // 8 bits for various flags
} ExampleStruct3;

#endif // EXAMPLE_STRUCTS_H
