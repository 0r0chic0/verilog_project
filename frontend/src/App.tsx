import React from "react"
import {Box} from "@chakra-ui/react"
import EditBox from "./EditBox"

function App() {
    return <Box minH="100vh" bg='#0f0a19' px={6} py={8} >
        <EditBox language="verilog" />
    </Box>
}
export default App;