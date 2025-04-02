#include <iostream>
#include <winsock2.h>

#define port 8080
#define BUFFER_SIZE 1024

int main(){
    WSADATA wsaData;
    SOCKET serverSocket, clientSocket;

    struct sockaddr_in serverAddr, clientAddr;
    int addrLen = sizeof(clientAddr);
    char buffer[BUFFER_SIZE] = {0};

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Falha ao inicializar Winsock\n";
        return -1;
    }

}